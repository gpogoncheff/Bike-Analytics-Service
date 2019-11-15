FROM ubuntu:18.04

RUN apt-get update -y && \
    apt-get install -y python3 python3-pip python3-pika python3-pillow

RUN apt-get update -y

RUN pip3 install pika --upgrade
RUN pip3 install numpy
RUN pip3 install matplotlib
RUN pip3 install geopy
RUN pip3 install --upgrade google-api-python-client
RUN pip3 install --upgrade google-cloud-storage
RUN pip3 install --upgrade google-cloud-datastore

WORKDIR /app
COPY . /app

CMD ["python3", "-u", "worker-serve.py"]