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
