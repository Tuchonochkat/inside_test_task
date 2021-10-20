FROM python:3.6
WORKDIR /app
COPY . .
RUN rm db.sqlite3
RUN pip install -r requirements.txt
ENTRYPOINT python manage.py runserver 0.0.0.0:8080