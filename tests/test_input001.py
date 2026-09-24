import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class Input001Tests(unittest.TestCase):
    def run_assess(self, raw: bytes, *extra):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "input.json"
            path.write_bytes(raw)
            return subprocess.run(
                [sys.executable, str(ROOT / "scripts/assess.py"), str(path), *extra],
                capture_output=True,
                text=True,
            )

    def test_duplicate_keys_rejected_recursively(self):
        version = json.loads((ROOT / "data/meta.json").read_text())["version"]
        cases = [
            (f'{{"assessment_id":"SVC","assessment_id":"SVC","version":"{version}","answers":{{}}}}', "assessment_id"),
            (f'{{"assessment_id":"SVC","version":"{version}","answers":{{"O01":"UNKNOWN","O01":"CLAIMED"}}}}', "O01"),
            (f'{{"assessment_id":"SVC","version":"{version}","answers":{{"O01":{{"state":"UNKNOWN","state":"CLAIMED"}}}}}}', "state"),
        ]
        for raw, key in cases:
            result = self.run_assess(raw.encode())
            self.assertNotEqual(result.returncode, 0)
            self.assertIn(f"duplicate JSON key rejected: {key}", result.stdout + result.stderr)

    def test_nonstandard_constants_and_extra_root_rejected(self):
        version = json.loads((ROOT / "data/meta.json").read_text())["version"]
        for value in ("NaN", "Infinity", "-Infinity"):
            raw = f'{{"assessment_id":"SVC","version":"{version}","answers":{{"O01":{value}}}}}'.encode()
            result = self.run_assess(raw)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("nonstandard JSON constant rejected", result.stdout + result.stderr)
        result = self.run_assess(json.dumps({"assessment_id":"SVC","version":version,"answers":{},"score":100}).encode())
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unsupported top-level fields: score", result.stdout + result.stderr)

    def test_invalid_utf8_and_size_cap(self):
        result = self.run_assess(b"\xff\xfe{}")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("valid UTF-8", result.stdout + result.stderr)
        result = self.run_assess(b" " * (1024 * 1024 + 1))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("exceeds 1048576 byte limit", result.stdout + result.stderr)

    def test_input_pilot_and_committed_reports(self):
        result = subprocess.run(
            [sys.executable, str(ROOT / "pilots/INPUT-001/run_input_pilot.py"), "--check"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
