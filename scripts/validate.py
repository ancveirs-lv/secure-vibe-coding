from __future__ import annotations
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def load(p): return json.loads((ROOT/p).read_text(encoding="utf-8"))

def validate():
    e=[]
    m=load("data/meta.json")
    en=load("data/assessment.en.json")
    lv=load("data/assessment.lv.json")
    src=load("data/sources.json")
    se=load("data/slop-indicators.en.json")
    sl=load("data/slop-indicators.lv.json")

    if en.get("canonical_language")!="en" or lv.get("canonical_language")!="en":
        e.append("canonical language contract failed")
    if en.get("version")!=m["version"] or lv.get("version")!=m["version"]:
        e.append("assessment version parity failed")
    if len(en["items"])!=m["expected_item_count"] or len(lv["items"])!=m["expected_item_count"]:
        e.append("item count failed")
    if len(en["domains"])!=m["expected_domain_count"] or len(lv["domains"])!=m["expected_domain_count"]:
        e.append("domain count failed")
    if [x["id"] for x in en["items"]] != [x["id"] for x in lv["items"]]:
        e.append("item parity failed")
    if [x["id"] for x in en["domains"]] != m["domain_ids"] or [x["id"] for x in lv["domains"]] != m["domain_ids"]:
        e.append("domain contract failed")
    if [x["id"] for x in en["states"]] != m["state_ids"] or [x["id"] for x in lv["states"]] != m["state_ids"]:
        e.append("state contract failed")
    if len(se["indicators"])!=m["expected_slop_indicator_count"] or len(sl["indicators"])!=m["expected_slop_indicator_count"]:
        e.append("slop indicator count failed")
    if se.get("version") != m["version"] or sl.get("version") != m["version"]:
        e.append("slop indicator version parity failed")
    if [x["id"] for x in se["indicators"]] != [x["id"] for x in sl["indicators"]]:
        e.append("slop indicator parity failed")

    valid=set(src["sources"])
    ranks=m["state_rank"]
    for lang,a in (("en",en),("lv",lv)):
        for state in a["states"]:
            if not state.get("meaning"): e.append(f"{lang}: missing state meaning: {state.get('id')}")
        for x in a["items"]:
            if x["domain"] not in m["domain_ids"]: e.append(f"{lang}:{x['id']}: invalid domain")
            if x["required_state"] not in ranks: e.append(f"{lang}:{x['id']}: invalid required_state")
            if not isinstance(x.get("release_blocking"),bool): e.append(f"{lang}:{x['id']}: release_blocking not boolean")
            if not isinstance(x.get("na_allowed"),bool): e.append(f"{lang}:{x['id']}: na_allowed not boolean")
            if not x.get("prompt") or not x.get("recommended_action") or not x.get("evidence_examples"):
                e.append(f"{lang}:{x['id']}: missing content")
            if not x.get("source_refs") or any(r not in valid for r in x["source_refs"]):
                e.append(f"{lang}:{x['id']}: invalid source refs")

    if m.get("global_english"):
        blob=json.dumps(en,ensure_ascii=False).lower()
        for bad in ("cert.lv","latvij"):
            if bad in blob: e.append(f"global English boundary failed: {bad}")

    return e

def main():
    e=validate()
    if e:
        print(f"Validation failed with {len(e)} error(s):")
        for x in e: print(f"- {x}")
        return 1
    m=load("data/meta.json")
    print(f"Validation passed: {m['expected_item_count']} bilingual controls, {m['expected_domain_count']} domains, {m['expected_slop_indicator_count']} bilingual slop indicators, parity, source and release-gate contracts.")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
