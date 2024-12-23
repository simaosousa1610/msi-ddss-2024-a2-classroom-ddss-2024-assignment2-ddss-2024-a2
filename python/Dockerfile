#
# Authors: Simão Sousa, simaosousa@student.dei.uc.pt
#

FROM python:3.12-alpine3.18

RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev openssl

RUN pip install flask==3.0.0

RUN pip install flask-wtf

RUN pip install psycopg2-binary

RUN pip install argon2-cffi

RUN pip install python-dotenv

RUN pip install Flask-SQLAlchemy

RUN pip install bleach

COPY . /app

VOLUME ["/app"]

WORKDIR /app

RUN mkdir -p logs

EXPOSE 5000

CMD ["python", "app.py"]
