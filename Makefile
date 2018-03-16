PORT = 7878

serve: deps
	python3 main.py -p ${PORT}

serve-production: deps
	gunicorn --workers=4 --bind=:${PORT} main:flask_app --log-level=error --capture-output --access-logfile=/tmp/foo --error-logfile=/tmp/bar

deps:
	pip install -r requirements.txt
