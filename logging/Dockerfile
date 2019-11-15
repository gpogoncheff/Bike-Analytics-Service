FROM ubuntu:18.04

RUN apt-get update -y && \
    apt-get install -y python3 python3-pip python3-pika

RUN apt-get update -y

RUN pip3 install pika --upgrade

WORKDIR /app
COPY . /app

CMD ["python3", "-u", "logs.py"]
