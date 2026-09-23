from __future__ import annotations
import argparse,json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
def load(p): return json.loads((ROOT/p).read_text(encoding="utf-8"))

def render(lang):
    a=load(f"data/assessment.{lang}.json"); m=load("data/meta.json"); s=load(f"data/slop-indicators.{lang}.json")
    title=m[f"title_{lang}"]; note=m[f"method_note_{lang}"]; definition=m[f"anti_slop_definition_{lang}"]
    lines=[f"# {title}","",f"> {note}","",definition,"","## "+("Response states" if lang=="en" else "Atbilžu stāvokļi"),""]
    for st in a["states"]:
        lines.append(f"- `{st['id']}` — {st['label']}: {st['meaning']}")
    lines += ["","## "+("Controls" if lang=="en" else "Kontroles"),""]
    by={d["id"]:[] for d in a["domains"]}
    for x in a["items"]: by[x["domain"]].append(x)
    for d in a["domains"]:
        lines += [f"### {d['title']}",""]
        for x in by[d["id"]]:
            action="Recommended action" if lang=="en" else "Ieteiktā darbība"
            req="Release requirement" if lang=="en" else "Izlaišanas prasība"
            ev="Evidence examples" if lang=="en" else "Pierādījumu piemēri"
            src="Sources" if lang=="en" else "Avoti"
            na=("yes" if x["na_allowed"] else "no") if lang=="en" else ("jā" if x["na_allowed"] else "nē")
            lines += [f"#### {x['id']}","",x["prompt"],"",
                      f"**{action}:** {x['recommended_action']}","",
                      f"**{req}:** `{x['required_state']}` · blocking=`{str(x['release_blocking']).lower()}` · N/A={na}","",
                      f"**{ev}:** " + "; ".join(x["evidence_examples"]),"",
                      f"**{src}:** " + ", ".join(f"`{r}`" for r in x["source_refs"]),""]

    lines += ["","## Anti-AI-Slop "+("indicators" if lang=="en" else "indikatori"),""]
    for x in s["indicators"]: lines.append(f"- `{x['id']}` — {x['text']}")
    return "\n".join(lines).rstrip()+"\n"

def main():
    p=argparse.ArgumentParser(); p.add_argument("--check",action="store_true"); args=p.parse_args()
    stale=[]
    for lang,path in (("en",ROOT/"docs/en/baseline.md"),("lv",ROOT/"docs/lv/baseline.md")):
        expected=render(lang)
        if args.check:
            if not path.exists() or path.read_text(encoding="utf-8")!=expected: stale.append(str(path.relative_to(ROOT)))
        else:
            path.parent.mkdir(parents=True,exist_ok=True); path.write_text(expected,encoding="utf-8")
    if stale:
        print("Generated documentation is stale: "+", ".join(stale)); return 1
    print("Generated documentation check passed." if args.check else "Generated documentation written.")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
