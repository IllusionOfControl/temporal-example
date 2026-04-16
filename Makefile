up:
	docker compose up

down:
	docker compose down

build:
	docker compose build

lint:
	uv run ruff check .

format:
	uv run ruff format .

fix:
	uv run ruff check . --fix
	uv run ruff format .

test-docker:
	docker build --target test -t temporal-app-test .
	docker run --env-file=.env --rm temporal-app-test

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +