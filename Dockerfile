FROM python:3.6
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
RUN python manage.py makemigrations
RUN python manage.py migrate
ENTRYPOINT python manage.py runserver 0.0.0.0:8080