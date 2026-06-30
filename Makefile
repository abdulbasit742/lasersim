.PHONY: install test smoke validate all clean

install:
	pip install -r requirements.txt
	pip install -e .

test:
	pytest -q

smoke:
	python run_all.py

validate:
	python validate.py

all: install smoke validate test

clean:
	rm -f *.png
	find . -name __pycache__ -type d -exec rm -rf {} +
