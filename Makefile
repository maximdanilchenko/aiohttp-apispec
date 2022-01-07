test:
	pytest tests -x -v

upload:
	if [ -d dist ]; then rm -Rf dist; fi
	python setup.py sdist
	twine upload dist/*

format:
	isort .
	black --target-version py36 .

check_format:
	isort . --check --diff
	black . --check --diff
