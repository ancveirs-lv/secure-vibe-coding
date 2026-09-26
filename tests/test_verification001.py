import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class Verification001Tests(unittest.TestCase):
    def test_synthetic_pilot_and_committed_report(self):
        result = subprocess.run(
            [sys.executable, str(ROOT / "pilots/VERIFICATION-001/run_verification_pilot.py"), "--check"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_schema_declares_claimed_not_established_assurance(self):
        text = (ROOT / "docs/verification-record.schema.json").read_text(encoding="utf-8")
        self.assertIn('"claimed_assurance_class"', text)
        self.assertIn('"INDEPENDENTLY_VERIFIED"', text)
        self.assertNotIn('"release_authorized"', text)

    def test_verifier_hard_codes_no_security_escalation(self):
        text = (ROOT / "scripts/verify_verification.py").read_text(encoding="utf-8")
        self.assertIn('"real_world_identity_verified_by_tool": False', text)
        self.assertIn('"organizational_independence_verified_by_tool": False', text)
        self.assertIn('"evidence_truth_verified_by_tool": False', text)
        self.assertIn('"product_security_established": False', text)
        self.assertIn('"release_authorized": False', text)

    def test_verifier_binds_current_assessment_contract_and_subject_label(self):
        text = (ROOT / "scripts/verify_verification.py").read_text(encoding="utf-8")
        self.assertIn('meta["assessment_id"]', text)
        self.assertIn('meta["version"]', text)
        self.assertNotIn('record["assessment_version"] == "0.1.1"', text)
        self.assertIn('evidence_subject.get("repository_hint") == subject["repository_hint"]', text)


if __name__ == "__main__":
    unittest.main()
