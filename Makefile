install:
	poetry install --only main,qa,local

lint:
	 ruff check src/

format:
	 ruff check --fix src/
