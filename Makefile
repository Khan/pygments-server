PORT = 7878

serve: deps
	python3 main.py -p ${PORT}

serve-production: deps
	gunicorn --workers=4 --bind=:${PORT} main:flask_app --log-level=error --capture-output

deps:
	pip3 install -r requirements.txt
