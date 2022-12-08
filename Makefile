install:
	poetry install --only main,qa,local

lint:
	pycln -c src/ttrack
	black --check src/ttrack
	pflake8 src/ttrack
	mypy src/ttrack

format:
	pycln -a src/ttrack
	isort src/ttrack
	black src/ttrack
