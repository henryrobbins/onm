include .env
export

.PHONY: dist
dist:
	rm -rf dist/*
	python3 -m build
	twine upload dist/*

test:
	pytest -s onm/tests --client_id $(PLAID_CLIENT_ID) --secret $(PLAID_SECRET)

unit-test:
	pytest -m unit -s onm/tests

integration-test:
	pytest -m integration -s onm/tests --client_id $(PLAID_CLIENT_ID) --secret $(PLAID_SECRET)
