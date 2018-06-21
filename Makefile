FLASK_VARS:=FLASK_APP=mm/app.py
ENABLE_DEV:=FLASK_ENV=development
dev:
	 $(FLASK_VARS) $(ENABLE_DEV) flask run


## DATABASE
ALEMBIC=PYTHONPATH=. alembic
reset-db:
	dropdb mm
	createdb mm
	$(ALEMBIC) upgrade head

auto-rev:
	$(ALEMBIC) revision --autogenerate

migrate:
	$(ALEMBIC) upgrade head
