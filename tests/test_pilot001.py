import subprocess
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

class Pilot001Tests(unittest.TestCase):
    def test_offline_pilot_and_committed_reports(self):
        p=subprocess.run(
            [sys.executable,str(ROOT/'pilots/PILOT-001/run_pilot.py'),'--check'],
            cwd=ROOT,capture_output=True,text=True,timeout=60
        )
        self.assertEqual(p.returncode,0,p.stdout+p.stderr)

if __name__=='__main__':
    unittest.main()
