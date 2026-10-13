# Futu OpenD Workflow for 0DTE Option Picks

Notes from a live 0DTE run on 2026-06-26 against SPY/QQQ/TSLA. The futu SDK
(`futu` 10.04.6408, OpenD port 11111) works for US option chains but has
several API traps that silently return ret=-1 or empty DataFrames. This
file captures the exact call sequence that works.

## Environment check

```bash
lsof -nP -iTCP:11111 -sTCP:LISTEN  # OpenD must be LISTEN
ps aux | grep -i "Futu_OpenD" | grep -v grep
```

If OpenD is not running, ask the user to launch Futu_OpenD.app before
proceeding — no fallback.

## Python connection boilerplate

```python
from futu import OpenQuoteContext, RET_OK
ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
ctx.set_handler(None)  # CRITICAL: suppresses async callback hang
```

`set_handler(None)` is what makes the synchronous calls actually return
on time. Without it, calls after the first one stall.

## Spot quote

`get_stock_quote()` returns empty DataFrames unpredictably. Always use
`get_market_snapshot()` — same fields, always populated.

```python
ret, sn = ctx.get_market_snapshot(['US.SPY'])
spot = sn.iloc[0]['last_price']
# useful cols: open_price, high_price, low_price, prev_close_price,
#   bid_price, ask_price, volume, update_time
```

## Option expiration dates

```python
ret, exps = ctx.get_option_expiration_date('US.SPY')
# returns DataFrame: strike_time | option_expiry_date_distance | expiration_cycle
# pick today for 0DTE (option_expiry_date_distance == 0)
```

## Option chain — THE TRAP

**Signature (Python inspect):**
```python
get_option_chain(self, code, index_option_type='NORMAL',
                 start=None, end=None, option_type='ALL',
                 option_cond_type='ALL', data_filter=None)
```

**Wrong (returns ret=-1, "the type of index_option_type param is wrong"):**
```python
ctx.get_option_chain('US.SPY', '2026-06-26')  # date string into index_option_type slot
```

**Wrong (hangs indefinitely — `IndexOptionType.ETF` does not exist):**
```python
from futu import IndexOptionType
ctx.get_option_chain('US.SPY', IndexOptionType.ETF, '2026-06-26')
```

**Right:**
```python
ret, chain = ctx.get_option_chain(
    code,
    index_option_type='NORMAL',        # pass string, not enum
    start='2026-06-26', end='2026-06-26',
    option_type='ALL', option_cond_type='ALL',
)
# chain is DataFrame; key cols: code, option_type (CALL/PUT),
#   strike_price, strike_time, stock_owner (=US.SPY)
```

## Per-strike snapshot

Do NOT construct option codes by hand (`US.SPY260626C73400` returns
"未知股票"). Read `chain.iloc[i]['code']` and snapshot that.

```python
near_codes = [r['code'] for r in chain.to_dict('records')
              if r['strike_price'] in near_strike_set]
ret, sn2 = ctx.get_market_snapshot(near_codes)
# key cols: code, last_price, bid_price, ask_price, bid_vol, ask_vol,
#   option_strike_price, option_type, option_open_interest,
#   option_implied_volatility, option_delta, option_gamma,
#   option_vega, option_theta, option_expiry_date_distance,
#   option_contract_multiplier
```

## Filtering criteria used in the 2026-06-26 run

- `|dist_pct| < 1.5` (strike within ±1.5% of spot)
- `OI > 200` (avoid illiquid strikes)
- `spread_pct < 30%` (filter junk mid prices on wide books)
- `IV > 0` (skip rows where futu returns NaN IV)

## Black-Scholes cross-check

For 0DTE same-day, use `T = 4/24/252` (≈4 hours to close). Risk-free
rate ≈ 4.5% as of mid-2026 (was 5.3% in the original skill text).

```python
import math
from scipy.stats import norm
S, K, T, r = spot, strike, 4.0/(24*252), 0.045
q = 0.013 if symbol in ('SPY','QQQ') else 0.01  # ETF vs equity dividend
sigma = iv_market / 100.0
d1 = (math.log(S/K) + (r - q + 0.5*sigma**2)*T) / (sigma*math.sqrt(T))
d2 = d1 - sigma*math.sqrt(T)
if is_call:
    bs_price = S*math.exp(-q*T)*norm.cdf(d1) - K*math.exp(-r*T)*norm.cdf(d2)
    bs_delta = math.exp(-q*T)*norm.cdf(d1)
else:
    bs_price = K*math.exp(-r*T)*norm.cdf(-d2) - S*math.exp(-q*T)*norm.cdf(-d1)
    bs_delta = -math.exp(-q*T)*norm.cdf(-d1)
```

Market `delta` is typically 10–30% off BS `delta` near expiry because
the market IV input is itself noisy on 0DTE. Treat BS as sanity-check
only, never as the pricing input.

## What `options-strategy-advisor` SKILL.md does NOT cover

The original skill assumes FMP API + manual IV entry. When running on
Futu OpenD, treat the BS computation as a final cross-check, not the
primary price — use `bid/ask mid` from futu as the entry assumption.

## Cleanup

Always `ctx.close()` in a `finally:` block. Background threads will
keep the OpenD conn slot occupied otherwise, and Futu's lock files
will block subsequent contexts.