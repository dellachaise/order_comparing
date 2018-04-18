.PHONY: backend

backend:
	cd backend; source ./env/bin/activate; python ./manage.py runserver
