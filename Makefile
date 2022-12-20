.PHONY: test

run:
	uvicorn main:app --reload

save:
	pip freeze > requirements.txt

install:
	pip install -r requirements.txt

test:
	PYTHONPATH=$(CURDIR) pytest -m"not aws" --cov --cov-report=xml -s .

test-all:
	PYTHONPATH=$(CURDIR) pytest --cov --cov-report=xml -s .