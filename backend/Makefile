.PHONY: test

run:
	uvicorn main:app --reload

save:
	pip freeze > requirements.txt

install:
	pip install -r requirements.txt

test:
	PYTHONPATH=$(CURDIR) pytest --cov --cov-report=xml -s .
