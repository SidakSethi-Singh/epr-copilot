.PHONY: test eval run docker sam-build

test:
	pytest tests/ -v --tb=short

eval:
	pytest tests/test_eval.py -v -s

run:
	python app.py

docker:
	docker build -t epr-copilot .

sam-build:
	sam build
