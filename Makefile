api:
	cd apps/api && uvicorn app.main:app --reload --port 8000

web:
	cd apps/web && npm run dev

install-api:
	cd apps/api && python -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt

install-web:
	cd apps/web && npm install

test-api:
	cd apps/api && pytest

dev-docker:
	docker compose up --build

stop-docker:
	docker compose down

reset-docker:
	docker compose down -v
	rm -rf storage
