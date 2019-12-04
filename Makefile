# DOCKER TASKS

build: ## Build the container
	docker build -t aiohttp-pg .

build-nc: ## Build the container without caching
	docker build --no-cache -t aiohttp-pg .

compose-up-clean: ## use docker compose to start the "-clean" service
	docker-compose up --remove-orphans aiohttp-pg-clean

compose-down:
	docker-compose down --remove-orphans
