include .env
export

.PHONY: dist
dist:
	rm -rf dist/*
	python3 -m build
	twine upload dist/*

test:
	coverage run -m pytest -s onm/tests --client_id $(PLAID_CLIENT_ID) --secret $(PLAID_SECRET)

unit-test:
	coverage run -m pytest -m unit -s onm/tests

integration-test:
	coverage run -m pytest -m integration -s onm/tests --client_id $(PLAID_CLIENT_ID) --secret $(PLAID_SECRET)

coverage-report:
	coverage report --include=onm/*

html-coverage:
	coverage html
	open htmlcov/index.html
