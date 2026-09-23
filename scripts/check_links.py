from __future__ import annotations
import json,urllib.request,urllib.error
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
    src=json.loads((ROOT/"data/sources.json").read_text(encoding="utf-8"))["sources"]
    bad=[]
    for k,v in src.items():
        req=urllib.request.Request(v["url"],headers={"User-Agent":"secure-vibe-coding-link-check/0.1"})
        try:
            with urllib.request.urlopen(req,timeout=20) as r:
                code=r.status
            print(f"OK   {code} {k}: {v['url']}")
        except urllib.error.HTTPError as e:
            if e.code in (403,429,999):
                print(f"WARN {e.code} {k}: rate-limited or bot-blocked")
            else:
                print(f"FAIL {e.code} {k}: {v['url']}"); bad.append(k)
        except Exception as e:
            print(f"FAIL {k}: {e}"); bad.append(k)
    if bad: return 1
    print("Source link health passed."); return 0
if __name__=="__main__": raise SystemExit(main())
