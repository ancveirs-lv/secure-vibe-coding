import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.verify_evidence import EvidenceError, decode_json, safe_git_path


class Evidence001UnitTests(unittest.TestCase):
    def test_duplicate_keys_are_rejected_in_nested_data(self):
        with self.assertRaisesRegex(EvidenceError, "duplicate JSON key rejected"):
            decode_json(b'{"subject": {"commit": "abc", "commit": "def"}}', "test")

    def test_path_hardening(self):
        for bad in ("../secret", "/absolute", "a//b", "a/./b", "a/../b", "a\\b", "a\nb"):
            with self.subTest(path=bad), self.assertRaises(EvidenceError):
                safe_git_path(bad)

    def test_synthetic_pilot_and_committed_report(self):
        run = subprocess.run(
            [sys.executable, str(ROOT / "pilots/EVIDENCE-001/run_evidence_pilot.py"), "--check"],
            capture_output=True, text=True, timeout=80, check=False,
        )
        self.assertEqual(run.returncode, 0, run.stderr + run.stdout)
        self.assertIn("EVIDENCE-001 PASS", run.stdout)


if __name__ == "__main__":
    unittest.main()
