FROM ubuntu:jammy

RUN mkdir code
WORKDIR code

ADD . /code/
ADD .env.docker /code/.env

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y python3 python3-pip
RUN pip install -r requirements.txt

CMD gunicorn booking.wsgi:application -b 0.0.0.0:8000