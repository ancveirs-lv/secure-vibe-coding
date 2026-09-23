from __future__ import annotations
import argparse,json
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
def load(p): return json.loads((ROOT/p).read_text(encoding="utf-8"))

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("answers"); ap.add_argument("--lang",choices=("en","lv"),default="en"); args=ap.parse_args()
    a=load(f"data/assessment.{args.lang}.json"); m=load("data/meta.json")
    payload=json.loads(Path(args.answers).read_text(encoding="utf-8"))
    supplied=payload.get("answers",{})
    valid=set(m["state_ids"]); ranks=m["state_rank"]
    gaps=[]; blocking=[]; all_states=[]; na_items=[]; unknown=[]
    for x in a["items"]:
        raw=supplied.get(x["id"],"UNKNOWN")
        if isinstance(raw,dict):
            state=raw.get("state","UNKNOWN"); note=str(raw.get("note","")).strip(); evidence=str(raw.get("evidence","")).strip()
        else:
            state=raw; note=""; evidence=""
        if state not in valid: raise SystemExit(f"invalid state for {x['id']}: {state}")
        if state=="VERIFIED" and not evidence:
            raise SystemExit(f"VERIFIED requires evidence for {x['id']}")
        if state=="NOT_APPLICABLE":
            if not x["na_allowed"]: raise SystemExit(f"NOT_APPLICABLE is not allowed for {x['id']}")
            if not note: raise SystemExit(f"NOT_APPLICABLE requires note for {x['id']}")
            na_items.append({"id":x["id"],"note":note}); all_states.append(state); continue
        all_states.append(state)
        if state=="UNKNOWN": unknown.append(x["id"])
        meets=ranks[state] >= ranks[x["required_state"]]
        if not meets:
            g={"id":x["id"],"domain":x["domain"],"state":state,"required_state":x["required_state"],"priority":x["priority"],"release_blocking":x["release_blocking"],"recommended_action":x["recommended_action"]}
            gaps.append(g)
            if x["release_blocking"]: blocking.append(g)
    gate="BLOCKED" if blocking else ("CONDITIONAL" if gaps else "READY")
    result={
        "assessment_id":a["assessment_id"],"version":a["version"],"language":args.lang,
        "gate":gate,"overall_state_counts":dict(Counter(all_states)),
        "unknown_items":unknown,"not_applicable_items":na_items,
        "blocking_gaps":blocking,"all_gaps":gaps,
        "note":"No aggregate security, compliance or maturity score is produced."
    }
    print(json.dumps(result,ensure_ascii=False,indent=2)); return 0

if __name__=="__main__":
    raise SystemExit(main())
