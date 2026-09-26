PYTHON ?= python3

validate:
	$(PYTHON) scripts/validate.py

render:
	$(PYTHON) scripts/render.py

check:
	$(PYTHON) scripts/validate.py
	$(PYTHON) scripts/render.py --check
	$(PYTHON) -m unittest discover -s tests -v

assess:
	$(PYTHON) scripts/assess.py examples/answers.example.json

pilot:
	$(PYTHON) pilots/PILOT-001/run_pilot.py --check

evidence:
	$(PYTHON) pilots/EVIDENCE-001/run_evidence_pilot.py --check

input:
	$(PYTHON) pilots/INPUT-001/run_input_pilot.py --check

verification:
	$(PYTHON) pilots/VERIFICATION-001/run_verification_pilot.py --check
