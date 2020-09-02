FROM python:3.8

ENV PYTHONUNBUFFERED 1
WORKDIR /project

COPY requirements.txt /project

RUN apt-get update
RUN apt-get -y install zip

RUN pip install -r requirements.txt
COPY . /project
