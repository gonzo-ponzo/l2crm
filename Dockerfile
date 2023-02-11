FROM python:3.10-alpine

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

RUN apk --update add
RUN apk add gcc libc-dev libffi-dev jpeg-dev zlib-dev libjpeg
RUN apk add postgresql-dev

RUN pip install --upgrade pip
COPY ./entrypoint.sh .

RUN chmod +x entrypoint.sh

COPY ./requirements.txt .

RUN pip install -r requirements.txt

COPY . .

RUN chmod +x entrypoint.sh
