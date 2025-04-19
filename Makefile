runserver:
	uv run python manage.py runserver

startapp:
	uv run python manage.py startapp $(name)