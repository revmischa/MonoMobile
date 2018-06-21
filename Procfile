web: gunicorn mm:app --preload --log-file=-
release: PYTHONPATH=. alembic upgrade head
