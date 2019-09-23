test:
	pytest tests -x -v

upload:
	if [ -d dist ]; then rm -Rf dist; fi
	python setup.py sdist
	twine upload dist/*

format:
	isort -y
	black --target-version py35 .

check_format:
	isort --check --diff
	black . --check --diff
