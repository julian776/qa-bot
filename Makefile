PHONY: setup
setup:
	cd backend && python3 -m venv .venv
	cd backend && source .venv/bin/activate && pip3 install -r requirements.txt
	cd frontend && npm install

.PHONY: pip
pip:
	@./scripts/pip.sh $(filter-out $@,$(MAKECMDGOALS))
	make freeze

.PHONY: freeze
freeze:
	cd backend && source .venv/bin/activate && pip freeze > requirements.txt

.PHONY: build
build:
	docker compose build

.PHONY: up
up:
	docker compose up -d

.PHONY: down
down:
	docker compose down

.PHONY: restart
restart: down build up

.PHONY: logs
logs:
	docker compose logs -f