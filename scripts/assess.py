from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAX_INPUT_BYTES = 1024 * 1024


class AssessmentInputError(ValueError):
    pass


def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise AssessmentInputError(f"duplicate JSON key rejected: {key}")
        result[key] = value
    return result


def reject_nonstandard_constant(value):
    raise AssessmentInputError(f"nonstandard JSON constant rejected: {value}")


def load_assessment_input(path: Path):
    if not path.is_file():
        raise SystemExit(f"assessment input not found: {path}")
    size = path.stat().st_size
    if size > MAX_INPUT_BYTES:
        raise SystemExit(
            f"assessment input exceeds {MAX_INPUT_BYTES} byte limit"
        )
    try:
        raw = path.read_bytes()
        text = raw.decode("utf-8")
        return json.loads(
            text,
            object_pairs_hook=unique_pairs,
            parse_constant=reject_nonstandard_constant,
        )
    except UnicodeDecodeError as exc:
        raise SystemExit(f"assessment input must be valid UTF-8: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid assessment JSON: {exc}") from exc
    except AssessmentInputError as exc:
        raise SystemExit(str(exc)) from exc


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("answers")
    parser.add_argument("--lang", choices=("en", "lv"), default="en")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--fail-on-blocked", action="store_true")
    mode.add_argument("--require-ready", action="store_true")
    args = parser.parse_args()

    assessment = load(f"data/assessment.{args.lang}.json")
    meta = load("data/meta.json")
    payload = load_assessment_input(Path(args.answers))

    if not isinstance(payload, dict):
        raise SystemExit("assessment input must be a JSON object")
    if payload.get("assessment_id") != meta["assessment_id"]:
        raise SystemExit("assessment_id mismatch")
    if payload.get("version") != meta["version"]:
        raise SystemExit("version mismatch")

    root_extra = set(payload) - {"assessment_id", "version", "answers"}
    if root_extra:
        raise SystemExit(
            "unsupported top-level fields: " + ", ".join(sorted(root_extra))
        )

    supplied = payload.get("answers")
    if not isinstance(supplied, dict):
        raise SystemExit("answers must be a JSON object")

    items = assessment["items"]
    known_ids = {item["id"] for item in items}
    unknown_ids = set(supplied) - known_ids
    if unknown_ids:
        raise SystemExit("unknown control IDs: " + ", ".join(sorted(unknown_ids)))

    valid = set(meta["state_ids"])
    ranks = meta["state_rank"]
    gaps, blocking, all_states, na_items, unknown = [], [], [], [], []

    for item in items:
        raw = supplied.get(item["id"], "UNKNOWN")
        if isinstance(raw, dict):
            extra_fields = set(raw) - {"state", "note", "evidence"}
            if extra_fields:
                raise SystemExit(
                    f"unsupported answer fields for {item['id']}: "
                    + ", ".join(sorted(extra_fields))
                )
            state = raw.get("state", "UNKNOWN")
            note = raw.get("note", "")
            evidence = raw.get("evidence", "")
            if not isinstance(note, str) or not isinstance(evidence, str):
                raise SystemExit(f"notes and evidence must be strings for {item['id']}")
            note = note.strip()
            evidence = evidence.strip()
        else:
            state, note, evidence = raw, "", ""

        if not isinstance(state, str) or state not in valid:
            raise SystemExit(f"invalid state for {item['id']}: {state}")
        if state == "VERIFIED" and not evidence:
            raise SystemExit(f"VERIFIED requires evidence for {item['id']}")
        if state == "NOT_APPLICABLE":
            if not item["na_allowed"]:
                raise SystemExit(f"NOT_APPLICABLE is not allowed for {item['id']}")
            if not note:
                raise SystemExit(f"NOT_APPLICABLE requires note for {item['id']}")
            na_items.append({"id": item["id"], "note": note})
            all_states.append(state)
            continue

        all_states.append(state)
        if state == "UNKNOWN":
            unknown.append(item["id"])

        if ranks[state] < ranks[item["required_state"]]:
            gap = {
                "id": item["id"],
                "domain": item["domain"],
                "state": state,
                "required_state": item["required_state"],
                "priority": item["priority"],
                "release_blocking": item["release_blocking"],
                "recommended_action": item["recommended_action"],
            }
            gaps.append(gap)
            if item["release_blocking"]:
                blocking.append(gap)

    gate = "BLOCKED" if blocking else ("CONDITIONAL" if gaps else "READY")
    result = {
        "assessment_id": assessment["assessment_id"],
        "version": assessment["version"],
        "language": args.lang,
        "gate": gate,
        "overall_state_counts": dict(Counter(all_states)),
        "unknown_items": unknown,
        "not_applicable_items": na_items,
        "blocking_gaps": blocking,
        "all_gaps": gaps,
        "input_contract": {
            "duplicate_json_keys": "rejected",
            "nonstandard_json_constants": "rejected",
            "unknown_top_level_fields": "rejected",
            "max_input_bytes": MAX_INPUT_BYTES,
        },
        "note": (
            "Evidence notes are self-reported and not validated automatically. "
            "No aggregate security, compliance or maturity score is produced."
        ),
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if args.require_ready and gate != "READY":
        return 2
    if args.fail_on_blocked and gate == "BLOCKED":
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
