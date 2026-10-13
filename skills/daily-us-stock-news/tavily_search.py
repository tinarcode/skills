#!/usr/bin/env python3
"""Tavily search helper - posts directly and saves results to /tmp."""
import json, sys, os, urllib.request, datetime

KEY = "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"

def search(query, max_results=5, depth="advanced"):
    body = json.dumps({
        "api_key": KEY,
        "query": query,
        "max_results": max_results,
        "search_depth": depth,
        "include_answer": True,
    }).encode()
    req = urllib.request.Request(
        "https://api.tavily.com/search",
        data=body,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())

if __name__ == "__main__":
    query = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else "/tmp/tavily_out.json"
    depth = sys.argv[3] if len(sys.argv) > 3 else "advanced"
    n = int(sys.argv[4]) if len(sys.argv) > 4 else 6
    data = search(query, max_results=n, depth=depth)
    with open(out, "w") as f:
        json.dump({"ts": datetime.datetime.now().isoformat(), "query": query, "result": data}, f, indent=2)
    ans = data.get("answer", "") or ""
    print(f"ANSWER: {ans[:600]}")
    print("---RESULTS---")
    for r in data.get("results", []):
        print(f"- {r['title']}")
        print(f"  {r['url']}")
        print(f"  {(r.get('content') or '')[:250]}")
