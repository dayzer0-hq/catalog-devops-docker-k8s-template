IMAGE ?= catalog
TAG   ?= 0.1.0

.PHONY: help install test run build up down logs k8s-apply k8s-delete

help:
	@grep -E '^[a-z-]+:.*?##' $(MAKEFILE_LIST) | sed 's/:.*##/\t/'

install: ## install app + test dependencies into the active environment
	pip install -r requirements-dev.txt

test: ## run the test suite
	python -m pytest -q

run: ## run the service locally, no container
	PORT=8080 python -m flask --app app:create_app run --port 8080

build: ## build the container image
	docker build -t $(IMAGE):$(TAG) .

up: ## start app + database
	docker compose up --build

down: ## stop and remove the stack and its volume
	docker compose down -v

logs: ## tail the app logs
	docker compose logs -f app

k8s-apply: ## apply the manifests to the current kube context
	kubectl apply -f k8s/

k8s-delete:
	kubectl delete -f k8s/
