import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class Pilot002Tests(unittest.TestCase):
    def test_end_to_end_synthetic_chain_and_committed_report(self):
        result = subprocess.run(
            [sys.executable, str(ROOT / "pilots/PILOT-002/run_pilot.py"), "--check"],
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("PILOT-002 PASS", result.stdout)

    def test_report_preserves_assurance_boundaries(self):
        report = json.loads(
            (ROOT / "pilots/PILOT-002/reports/synthetic-results.json").read_text(encoding="utf-8")
        )
        self.assertEqual(report["result"], "PASS")
        self.assertEqual(report["stages"]["assessment"]["en_gate"], "READY")
        self.assertEqual(report["stages"]["assessment"]["lv_gate"], "READY")
        self.assertEqual(report["stages"]["evidence"]["artifact_binding"], "PASS")
        self.assertEqual(report["stages"]["verification"]["record_signature"], "PASS")
        self.assertEqual(report["stages"]["evidence"]["bound_control_count"], 32)
        self.assertEqual(report["stages"]["verification"]["verified_control_count"], 32)
        boundary = report["assurance_boundary"]
        self.assertTrue(boundary["synthetic_only"])
        self.assertFalse(boundary["real_world_identity_verified_by_tool"])
        self.assertFalse(boundary["organizational_independence_verified_by_tool"])
        self.assertFalse(boundary["evidence_truth_verified_by_tool"])
        self.assertFalse(boundary["product_security_established"])
        self.assertFalse(boundary["release_authorized"])


if __name__ == "__main__":
    unittest.main()
