#!/usr/bin/env python3
"""0DTE option screen via Futu OpenD.

Filters strikes within ±DIST_PCT% of spot, with OI > MIN_OI and bid-ask
spread < MAX_SPREAD_PCT. Cross-checks mid against Black-Scholes using
market IV. Writes JSON to /tmp/futu_0dte_screen.json.

Usage:
    python3 scripts/futu_0dte_screen.py
    python3 scripts/futu_0dte_screen.py --codes US.SPY US.QQQ --dist 1.0

Stdlib + numpy + scipy only. futu SDK must be importable from this
python (the user-installed system python; not hermes-agent's venv).
"""
import argparse, json, math, sys
from datetime import date

import numpy as np
from scipy.stats import norm

from futu import OpenQuoteContext, RET_OK

# 0DTE constants
T_0DTE = 4.0 / (24 * 252)   # ≈4h to close
R = 0.045                    # mid-2026 risk-free
Q = {"US.SPY": 0.013, "US.QQQ": 0.013, "US.TSLA": 0.01}


def fetch_chain(ctx, code, expiry):
    """Return (spot, list_of_strike_rows). Each row has strike, type, code,
    bid, ask, last, IV, OI, delta, gamma, vega, theta.
    """
    ret, sn = ctx.get_market_snapshot([code])
    if ret != RET_OK or len(sn) == 0:
        return None, []
    spot = float(sn.iloc[0]['last_price'])

    ret, chain = ctx.get_option_chain(
        code,
        index_option_type='NORMAL',
        start=expiry, end=expiry,
        option_type='ALL', option_cond_type='ALL',
    )
    if ret != RET_OK:
        return spot, []

    rows = chain.to_dict('records')
    strikes = sorted({r['strike_price'] for r in rows})
    atm = min(strikes, key=lambda s: abs(s - spot))
    return spot, rows, atm


def bs_price_delta(spot, strike, otype, iv_pct, q=0.0):
    sigma = iv_pct / 100.0 if iv_pct and iv_pct > 0 else None
    if sigma is None:
        return None, None
    d1 = (math.log(spot/strike) + (R - q + 0.5*sigma**2)*T_0DTE) / (sigma*math.sqrt(T_0DTE))
    d2 = d1 - sigma*math.sqrt(T_0DTE)
    if otype == 'CALL':
        return (spot*math.exp(-q*T_0DTE)*norm.cdf(d1)
                - strike*math.exp(-R*T_0DTE)*norm.cdf(d2),
                math.exp(-q*T_0DTE)*norm.cdf(d1))
    return (strike*math.exp(-R*T_0DTE)*norm.cdf(-d2)
            - spot*math.exp(-q*T_0DTE)*norm.cdf(-d1),
            -math.exp(-q*T_0DTE)*norm.cdf(-d1))


def screen(args):
    today = args.expiry or date.today().isoformat()
    out = {}
    ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
    ctx.set_handler(None)
    try:
        for code in args.codes:
            res = fetch_chain(ctx, code, today)
            if len(res) == 2:
                spot, rows = res
                atm = None
            else:
                spot, rows, atm = res
            q = Q.get(code, 0.0)
            near = sorted({r['strike_price'] for r in rows},
                          key=lambda s: abs(s - spot))[:args.num_strikes]
            near_codes = [r['code'] for r in rows if r['strike_price'] in near]
            if not near_codes:
                out[code] = {'spot': spot, 'rows': []}
                continue
            ret, sn = ctx.get_market_snapshot(near_codes)
            if ret != RET_OK or len(sn) == 0:
                out[code] = {'spot': spot, 'rows': []}
                continue
            keep = ['code','last_price','bid_price','ask_price','bid_vol','ask_vol',
                    'option_strike_price','option_type','option_open_interest',
                    'option_implied_volatility','option_delta','option_gamma',
                    'option_vega','option_theta']
            sn = sn[[c for c in keep if c in sn.columns]]
            out_rows = []
            for _, r in sn.iterrows():
                K = float(r['option_strike_price'])
                otype = r['option_type']
                bid = float(r['bid_price'] or 0)
                ask = float(r['ask_price'] or 0)
                last = float(r['last_price'] or 0)
                mid = (bid + ask) / 2 if bid and ask else last
                spread_pct = ((ask - bid) / mid * 100) if mid and ask > bid else 999
                iv_pct = float(r['option_implied_volatility'] or 0)
                oi = int(r['option_open_interest'] or 0)
                if (abs(K/spot - 1) > args.dist/100
                        or oi < args.min_oi
                        or spread_pct > args.max_spread
                        or iv_pct <= 0):
                    continue
                bs_p, bs_d = bs_price_delta(spot, K, otype, iv_pct, q)
                out_rows.append({
                    'code': r['code'],
                    'type': 'C' if 'CALL' in str(otype) else 'P',
                    'strike': K,
                    'dist_pct': round((K/spot - 1) * 100, 3),
                    'mid': round(mid, 2) if mid else 0,
                    'spread_pct': round(spread_pct, 2),
                    'iv_pct': round(iv_pct, 2),
                    'oi': oi,
                    'delta_mkt': round(float(r['option_delta'] or 0), 4),
                    'delta_bs': round(bs_d, 4) if bs_d is not None else None,
                    'bs_price': round(bs_p, 2) if bs_p is not None else None,
                    'theta': round(float(r['option_theta'] or 0), 3),
                    'vega': round(float(r['option_vega'] or 0), 3),
                })
            out_rows.sort(key=lambda r: -r['oi'])
            out[code] = {
                'spot': spot,
                'atm': atm,
                'expiry': today,
                'rows': out_rows,
            }
    finally:
        ctx.close()

    out['_meta'] = {'expiry': today, 'T_years': T_0DTE, 'risk_free': R}
    with open(args.out, 'w') as f:
        json.dump(out, f, indent=2, default=str)
    print(f"WROTE {args.out} for {len(args.codes)} tickers, expiry {today}")
    for code in args.codes:
        d = out.get(code, {})
        print(f"  {code}: spot={d.get('spot')} atm={d.get('atm')} rows={len(d.get('rows', []))}")


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--codes', nargs='+', default=['US.SPY', 'US.QQQ', 'US.TSLA'])
    ap.add_argument('--expiry', default=None, help='YYYY-MM-DD; default = today')
    ap.add_argument('--dist', type=float, default=1.5, help='±%% from spot')
    ap.add_argument('--min-oi', type=int, default=200)
    ap.add_argument('--max-spread', type=float, default=30.0)
    ap.add_argument('--num-strikes', type=int, default=21)
    ap.add_argument('--out', default='/tmp/futu_0dte_screen.json')
    screen(ap.parse_args())