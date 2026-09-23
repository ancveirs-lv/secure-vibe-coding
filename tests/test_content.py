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
            p=Path(d)/"a.json"; p.write_text(json.dumps({"assessment_id":"SVC","version":"0.1.1","answers":{a["items"][0]["id"]:"VERIFIED"}}))
            r=subprocess.run([sys.executable,str(ROOT/"scripts/assess.py"),str(p)],capture_output=True,text=True)
            self.assertNotEqual(r.returncode,0); self.assertIn("requires evidence",r.stdout+r.stderr)
    def test_na_contract(self):
        a=load("data/assessment.en.json")
        disallowed=next(x for x in a["items"] if not x["na_allowed"])
        allowed=next(x for x in a["items"] if x["na_allowed"])
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"bad.json"; p.write_text(json.dumps({"assessment_id":"SVC","version":"0.1.1","answers":{disallowed["id"]:{"state":"NOT_APPLICABLE","note":"x"}}}))
            r=subprocess.run([sys.executable,str(ROOT/"scripts/assess.py"),str(p)],capture_output=True,text=True)
            self.assertNotEqual(r.returncode,0)
            p2=Path(d)/"good.json"; p2.write_text(json.dumps({"assessment_id":"SVC","version":"0.1.1","answers":{allowed["id"]:{"state":"NOT_APPLICABLE","note":"documented context"}}}))
            r2=subprocess.run([sys.executable,str(ROOT/"scripts/assess.py"),str(p2)],capture_output=True,text=True)
            self.assertEqual(r2.returncode,0,r2.stdout+r2.stderr)
    def test_ready_requires_all_requirements(self):
        a=load("data/assessment.en.json"); answers={}
        for x in a["items"]:
            answers[x["id"]]={"state":"VERIFIED","evidence":"test evidence"}
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"ready.json"; p.write_text(json.dumps({"assessment_id":"SVC","version":"0.1.1","answers":answers}))
            r=subprocess.run([sys.executable,str(ROOT/"scripts/assess.py"),str(p)],capture_output=True,text=True)
            self.assertEqual(r.returncode,0,r.stdout+r.stderr); out=json.loads(r.stdout); self.assertEqual(out["gate"],"READY")
    def test_input_identity_and_unknown_id_fail_closed(self):
        base={"assessment_id":"SVC","version":"0.1.1","answers":{"O01":"IMPLEMENTED"}}
        for changed, message in (
            ({"assessment_id":"WRONG"},"assessment_id mismatch"),
            ({"version":"0.1.0"},"version mismatch"),
            ({"answers":{"O0X":"VERIFIED"}},"unknown control IDs"),
            ({"answers":[]},"answers must be a JSON object"),
        ):
            payload={**base,**changed}
            with tempfile.TemporaryDirectory() as d:
                path=Path(d)/"invalid.json"
                path.write_text(json.dumps(payload),encoding="utf-8")
                run=subprocess.run([sys.executable,str(ROOT/"scripts/assess.py"),str(path)],capture_output=True,text=True)
                self.assertNotEqual(run.returncode,0,payload)
                self.assertIn(message,run.stdout+run.stderr)

    def test_blocked_and_ready_ci_exit_contracts(self):
        blocked=subprocess.run([sys.executable,str(ROOT/"scripts/assess.py"),str(ROOT/"examples/answers.example.json"),"--fail-on-blocked"],capture_output=True,text=True)
        self.assertEqual(blocked.returncode,2)
        self.assertEqual(json.loads(blocked.stdout)["gate"],"BLOCKED")
        required=subprocess.run([sys.executable,str(ROOT/"scripts/assess.py"),str(ROOT/"examples/answers.example.json"),"--require-ready"],capture_output=True,text=True)
        self.assertEqual(required.returncode,2)

    def test_code_license_complete(self):
        text=(ROOT/"LICENSE-CODE").read_text(encoding="utf-8")
        self.assertIn("The above copyright notice and this permission notice",text)
        self.assertIn('THE SOFTWARE IS PROVIDED "AS IS"',text)

    def test_all_machine_readable_versions_match(self):
        version=load("data/meta.json")["version"]
        for path in ("data/assessment.en.json","data/assessment.lv.json","data/slop-indicators.en.json","data/slop-indicators.lv.json","examples/answers.example.json"):
            self.assertEqual(load(path)["version"],version,path)
if __name__=="__main__": unittest.main()
