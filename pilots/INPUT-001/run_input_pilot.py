#!/usr/bin/env python3
"""INPUT-001 fail-closed assessment-input regression checks."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

PILOT = Path(__file__).resolve().parent
ROOT = PILOT.parents[1]
LANGS = ("en", "lv")
MAX_INPUT_BYTES = 1024 * 1024


def insist(condition, message):
    if not condition:
        raise AssertionError(message)


def invoke(path: Path, lang="en", flag=None):
    cmd = [sys.executable, str(ROOT / "scripts/assess.py"), str(path), "--lang", lang]
    if flag:
        cmd.append(flag)
    return subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=15)


def ready_payload():
    assessment = json.loads((ROOT / "data/assessment.en.json").read_text(encoding="utf-8"))
    version = json.loads((ROOT / "data/meta.json").read_text(encoding="utf-8"))["version"]
    return {
        "assessment_id": "SVC",
        "version": version,
        "answers": {
            item["id"]: {"state": "VERIFIED", "evidence": f"INPUT-001 SYNTHETIC TOKEN {item['id']}"}
            for item in assessment["items"]
        },
    }


def rejected_case(path: Path, expected_phrase: str):
    for lang in LANGS:
        run = invoke(path, lang, "--require-ready")
        insist(run.returncode != 0, f"{path.name} {lang}: malformed input accepted")
        combined = run.stdout + run.stderr
        insist(expected_phrase in combined, f"{path.name} {lang}: unexpected rejection: {combined}")


def checks():
    base = ready_payload()
    negative = []
    with tempfile.TemporaryDirectory(prefix="svc-input001-") as tmp:
        td = Path(tmp)

        cases = {
            "duplicate_root.json": (
                '{"assessment_id":"SVC","assessment_id":"SVC","version":"%s","answers":{}}' % base["version"],
                "duplicate JSON key rejected: assessment_id",
            ),
            "duplicate_control.json": (
                '{"assessment_id":"SVC","version":"%s","answers":{"O01":"UNKNOWN","O01":"VERIFIED"}}' % base["version"],
                "duplicate JSON key rejected: O01",
            ),
            "duplicate_nested.json": (
                '{"assessment_id":"SVC","version":"%s","answers":{"O01":{"state":"UNKNOWN","state":"VERIFIED","evidence":"x"}}}' % base["version"],
                "duplicate JSON key rejected: state",
            ),
            "nan.json": (
                '{"assessment_id":"SVC","version":"%s","answers":{"O01":NaN}}' % base["version"],
                "nonstandard JSON constant rejected: NaN",
            ),
            "infinity.json": (
                '{"assessment_id":"SVC","version":"%s","answers":{"O01":Infinity}}' % base["version"],
                "nonstandard JSON constant rejected: Infinity",
            ),
            "extra_root.json": (
                json.dumps({**base, "score": 100}),
                "unsupported top-level fields: score",
            ),
            "scenario_metadata.json": (
                json.dumps({**base, "scenario_id": "ready"}),
                "unsupported top-level fields: scenario_id",
            ),
            "root_array.json": (
                "[]",
                "assessment input must be a JSON object",
            ),
        }
        for name, (content, phrase) in cases.items():
            p = td / name
            p.write_text(content, encoding="utf-8")
            rejected_case(p, phrase)
            negative.append(name)

        bad_utf8 = td / "bad_utf8.json"
        bad_utf8.write_bytes(b"\xff\xfe{\"assessment_id\":\"SVC\"}")
        rejected_case(bad_utf8, "assessment input must be valid UTF-8")
        negative.append(bad_utf8.name)

        too_large = td / "too_large.json"
        too_large.write_bytes(b" " * (MAX_INPUT_BYTES + 1))
        rejected_case(too_large, "assessment input exceeds")
        negative.append(too_large.name)

        valid = td / "ready.json"
        valid.write_text(json.dumps(base, ensure_ascii=False), encoding="utf-8")
        gates = {}
        contracts = []
        for lang in LANGS:
            plain = invoke(valid, lang)
            insist(plain.returncode == 0, plain.stderr)
            parsed = json.loads(plain.stdout)
            insist(parsed["gate"] == "READY", f"{lang}: valid READY changed")
            insist(parsed["input_contract"]["duplicate_json_keys"] == "rejected", "missing input contract")
            gates[lang] = parsed["gate"]
            strict = invoke(valid, lang, "--require-ready")
            insist(strict.returncode == 0, f"{lang}: READY strict exit changed")
            contracts.append({"language": lang, "gate": parsed["gate"], "require_ready_exit": strict.returncode})

        sparse = td / "sparse.json"
        sparse.write_text(json.dumps({"assessment_id": "SVC", "version": base["version"], "answers": {"O01": "CLAIMED"}}), encoding="utf-8")
        for lang in LANGS:
            run = invoke(sparse, lang, "--fail-on-blocked")
            insist(run.returncode == 2 and json.loads(run.stdout)["gate"] == "BLOCKED", f"{lang}: sparse fail-closed regression")

    return {
        "pilot_id": "INPUT-001",
        "result": "PASS",
        "scope": "assessment JSON parser and fail-closed input contract",
        "languages": list(LANGS),
        "negative_cases_rejected": negative,
        "negative_case_count": len(negative),
        "valid_ready_gates": gates,
        "strict_ready_contracts": contracts,
        "remediated_findings": [
            {
                "id": "LIM-DUPLICATE-003",
                "status": "REMEDIATED",
                "evidence": "duplicate keys rejected at root, answers map and nested answer object",
            }
        ],
        "residual_limitations": [
            "Evidence-note truth is not authenticated by assess.py.",
            "NOT_APPLICABLE rationale truth is not automatically validated.",
            "INPUT-001 validates syntax and contract semantics, not product security.",
        ],
        "release_claim": "Input-contract hardening only; no production security, evidence authenticity or deployment authorization conclusion.",
    }


def markdown(data, lang):
    if lang == "en":
        lines = [
            "# INPUT-001 — Fail-closed input results",
            "",
            "**Outcome: PASS for the assessment-input contract.**",
            "",
            f"Rejected negative cases: **{data['negative_case_count']}** in both EN/LV execution paths.",
            "",
            "- Duplicate JSON keys are rejected recursively.",
            "- `NaN` and `Infinity` are rejected.",
            "- Unknown top-level fields are rejected.",
            "- Invalid UTF-8 and inputs larger than 1 MiB are rejected.",
            "- Valid existing `READY` input remains `READY` in EN/LV.",
            "- Sparse valid input still produces `BLOCKED` under the strict CI gate.",
            "",
            "**LIM-DUPLICATE-003: REMEDIATED.** The original PILOT-001 finding remains documented as historical context.",
            "",
            "This does not authenticate evidence notes or prove software security.",
            "",
        ]
    else:
        lines = [
            "# INPUT-001 — Fail-closed ievades rezultāti",
            "",
            "**Rezultāts: PASS novērtējuma ievades kontraktam.**",
            "",
            f"Noraidīti negatīvie gadījumi: **{data['negative_case_count']}** abos EN/LV izpildes ceļos.",
            "",
            "- Atkārtotas JSON atslēgas tiek rekursīvi noraidītas.",
            "- `NaN` un `Infinity` tiek noraidīti.",
            "- Nezināmi augšējā līmeņa lauki tiek noraidīti.",
            "- Nederīgs UTF-8 un ievade virs 1 MiB tiek noraidīta.",
            "- Esoša derīga `READY` ievade paliek `READY` EN/LV.",
            "- Nepilnīga, bet sintaktiski derīga ievade stingrajā CI režīmā joprojām dod `BLOCKED`.",
            "",
            "**LIM-DUPLICATE-003: REMEDIATED.** Sākotnējais PILOT-001 atradums tiek saglabāts kā vēsturiska atsauce.",
            "",
            "Tas neapstiprina pierādījumu piezīmju patiesumu un nepierāda programmatūras drošību.",
            "",
        ]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--write", action="store_true")
    args = parser.parse_args()
    try:
        result = checks()
        outputs = {
            PILOT / "reports/results.json": json.dumps(result, ensure_ascii=False, indent=2) + "\n",
            PILOT / "reports/summary.en.md": markdown(result, "en"),
            PILOT / "reports/summary.lv.md": markdown(result, "lv"),
        }
        for path, content in outputs.items():
            if args.write:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content, encoding="utf-8")
            else:
                insist(path.is_file() and path.read_text(encoding="utf-8") == content, f"stale or missing report: {path.relative_to(ROOT)}")
    except (AssertionError, OSError, subprocess.TimeoutExpired) as exc:
        print(f"INPUT-001 FAIL: {exc}", file=sys.stderr)
        return 1
    print("INPUT-001 PASS: recursive duplicate-key rejection, strict JSON constants, top-level contract, UTF-8/size caps, EN/LV compatibility.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
