import json,subprocess,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT))
from scripts.validate import validate
def load(p): return json.loads((ROOT/p).read_text(encoding="utf-8"))

class Tests(unittest.TestCase):
    def test_validation(self): self.assertEqual(validate(),[])
    def test_item_count_parity(self):
        m=load("data/meta.json"); en=load("data/assessment.en.json"); lv=load("data/assessment.lv.json")
        self.assertEqual(len(en["items"]),32); self.assertEqual([x["id"] for x in en["items"]],[x["id"] for x in lv["items"]])
        self.assertEqual(m["expected_item_count"],32)
    def test_slop_indicator_parity(self):
        en=load("data/slop-indicators.en.json"); lv=load("data/slop-indicators.lv.json")
        self.assertEqual(len(en["indicators"]),16); self.assertEqual([x["id"] for x in en["indicators"]],[x["id"] for x in lv["indicators"]])
    def test_generated_docs(self):
        r=subprocess.run([sys.executable,str(ROOT/"scripts/render.py"),"--check"],capture_output=True,text=True)
        self.assertEqual(r.returncode,0,r.stdout+r.stderr)
    def test_example_is_blocked_and_has_no_score(self):
        r=subprocess.run([sys.executable,str(ROOT/"scripts/assess.py"),str(ROOT/"examples/answers.example.json")],capture_output=True,text=True)
        self.assertEqual(r.returncode,0,r.stdout+r.stderr); p=json.loads(r.stdout)
        self.assertEqual(p["gate"],"BLOCKED"); self.assertNotIn("score",p)
    def test_verified_requires_evidence(self):
        a=load("data/assessment.en.json")
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"a.json"; p.write_text(json.dumps({"answers":{a["items"][0]["id"]:"VERIFIED"}}))
            r=subprocess.run([sys.executable,str(ROOT/"scripts/assess.py"),str(p)],capture_output=True,text=True)
            self.assertNotEqual(r.returncode,0); self.assertIn("requires evidence",r.stdout+r.stderr)
    def test_na_contract(self):
        a=load("data/assessment.en.json")
        disallowed=next(x for x in a["items"] if not x["na_allowed"])
        allowed=next(x for x in a["items"] if x["na_allowed"])
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"bad.json"; p.write_text(json.dumps({"answers":{disallowed["id"]:{"state":"NOT_APPLICABLE","note":"x"}}}))
            r=subprocess.run([sys.executable,str(ROOT/"scripts/assess.py"),str(p)],capture_output=True,text=True)
            self.assertNotEqual(r.returncode,0)
            p2=Path(d)/"good.json"; p2.write_text(json.dumps({"answers":{allowed["id"]:{"state":"NOT_APPLICABLE","note":"documented context"}}}))
            r2=subprocess.run([sys.executable,str(ROOT/"scripts/assess.py"),str(p2)],capture_output=True,text=True)
            self.assertEqual(r2.returncode,0,r2.stdout+r2.stderr)
    def test_ready_requires_all_requirements(self):
        a=load("data/assessment.en.json"); answers={}
        for x in a["items"]:
            answers[x["id"]]={"state":"VERIFIED","evidence":"test evidence"}
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"ready.json"; p.write_text(json.dumps({"answers":answers}))
            r=subprocess.run([sys.executable,str(ROOT/"scripts/assess.py"),str(p)],capture_output=True,text=True)
            self.assertEqual(r.returncode,0,r.stdout+r.stderr); out=json.loads(r.stdout); self.assertEqual(out["gate"],"READY")
if __name__=="__main__": unittest.main()
