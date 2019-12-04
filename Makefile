# DOCKER TASKS
# Build the container
build: ## Build the container
	docker build -t aiohttp-pg .

build-nc: ## Build the container without caching
	docker build --no-cache -t aiohttp-pg .

run-local: ## Run container interactively, container dies on exit
	docker run -it aiohttp-pg python -m app -c config.local.json