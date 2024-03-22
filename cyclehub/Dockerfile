FROM python:3.8-buster

ENV PYTHONUNBUFFERED=1
RUN apt-get update -q && apt-get install -yq libpq-dev && apt-get install -y postgresql-client

WORKDIR /app 

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

EXPOSE 8000

# Run migrations before starting the server
CMD ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]
