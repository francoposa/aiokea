# DOCKER TASKS

build: ## Build the container
	docker build -t aiohttp-pg .

build-nc: ## Build the container without caching
	docker build --no-cache -t aiohttp-pg .

compose-up: ## use docker compose to start the main python service
	docker-compose up --remove-orphans aiohttp-pg

compose-down:
	docker-compose down --remove-orphans

compose-ci:
	docker-compose run --rm ci