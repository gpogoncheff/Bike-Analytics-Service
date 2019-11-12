from flask import Flask, request, Response
import jsonpickle
import numpy as np
from PIL import Image
import io
import hashlib
import pika
import pickle
import socket
import sys
from utils.Datastore import get_aggregate_statistics, get_ride_data

# Initialize the Flask application
app = Flask(__name__)


def publish_work_request(data, host='rabbitmq', queue_name='work_route'):
    success = False
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=host))
        channel = connection.channel()
        channel.queue_declare(queue=queue_name, durable=True)

        channel.basic_publish(
            exchange='',
            routing_key=queue_name,
            body=data,
            properties=pika.BasicProperties(delivery_mode=2)
        )
        success = True

    except pika.exceptions.AMQPConnectionError:
        # Debug
        print("Connection error")

    except pika.exceptions.AMPQChannelError:
        # Debug
        print("Channel Error")
        if connection is not None:
            connection.close()

    if connection is not None:
        connection.close()

    return success


def log_request(request, status):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
    log_channel = connection.channel()
    log_channel.exchange_declare(exchange='logs', exchange_type='topic')
    connection.close()

# Test route
@app.route('/', methods=['GET', 'POST'])
def test():
    return "Testing..."


@app.route('/upload-ride/<filename>', methods=['PUT'])
def process_data(filename):
    r = request
    try:
        hash = str(hashlib.md5(r.data).hexdigest())
        data = pickle.dumps((hash, filename, r.data))
        publish_work_request(data, host='localhost')
        response = {'md5 hash' : hash}
        status=200
    except BaseException as e:
        print('Error: upload-ride - {}'.format(e))
        response = { 'md5 hash' : 'None'}
        status=400

    return Response(response=jsonpickle.encode(response), status=status, mimetype="application/json")


@app.route('/global-stats', methods=['GET'])
def get_global_statistics():
    try:
        data = get_aggregate_statistics()
        status = 200
    except BaseException as e:
        print('Error: global-stats - {}'.format(e))
        data = {}
        status = 400

    return Response(response=jsonpickle.encode(data), status=status, mimetype="application/json")


@app.route('/ride-data/<digest>', methods=['GET'])
def get_data_for_ride(digest):
    try:
        data = get_ride_data(digest)
        status = 200
    except BaseException as e:
        print('Error: ride-data - {}'.format(e))
        data = []
        status = 400

    response = {'segments': data}
    return Response(response=jsonpickle.encode(data), status=status, mimetype="application/json")


@app.route('/visualize', methods=['GET'])
def get_ride_visualizations():
    return 'TODO...'


if __name__ == '__main__':
    # start flask app
    app.run(host="0.0.0.0", port=5000)
    connection.close()
