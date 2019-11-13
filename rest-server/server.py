from flask import Flask, request, Response, redirect
import jsonpickle
import numpy as np
from PIL import Image
import io
import hashlib
import pika
import pickle
import socket
import sys
import socket
from utils.Datastore import get_aggregate_statistics, get_ride_data
from utils.CloudStorage import get_visualization_url

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

    except (pika.exceptions.AMQPConnectionError, pika.exceptions.AMPQChannelError):
        # Debug
        print("AMPQ Error")
        success = False

    if connection is not None:
        connection.close()

    return success


def log_api_status(api, success, message='', host='rabbitmq'):
    # log the api that was called and the result of the api call
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=host))
        log_channel = connection.channel()
        log_channel.exchange_declare(exchange='logs', exchange_type='topic')

        log_channel.basic_publish(
            exchange='logs',
            routing_key='{}.rest.info'.format(socket.gethostname()),
            body='API Call: {} - {}'.format(api, message)
        )
        if not success:
            log_channel.basic_publish(
                exchange='logs',
                routing_key='{}.rest.debug'.format(socket.gethostname()),
                body='API Call: {} - FAILED; {}'.format(api, message)
            )
    except:
        print('Failed to log api info')

    if connection is not None:
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
        work_published = publish_work_request(data, host='localhost')
        response = {'md5 hash' : hash}
        status = 200 if work_published else 500
    except BaseException as e:
        print('Error: upload-ride - {}'.format(e))
        response = { 'md5 hash' : 'None'}
        status = 400

    success = False
    if status == 200:
        message = 'SUCCESS'
        success = True
    elif status == 500:
        message = 'Failed to publish to RabbitMQ'
    else:
        message = 'FAILED'
    log_api_status('/upload-ride/{}'.format(filename), success, message, host='localhost')

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

    success = False
    if status == 200:
        message = 'SUCCESS'
        success = True
    else:
        message = 'FAILED'
    log_api_status('/global-stats', success, message, host='localhost')

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

    success = False
    if status == 200:
        message = 'SUCCESS'
        success = True
    else:
        message = 'FAILED'
    log_api_status('/ride-data/{}'.format(digest), success, message, host='localhost')

    response = {'segments': data}
    return Response(response=jsonpickle.encode(response), status=status, mimetype="application/json")


@app.route('/visualize/<digest>/<segment>', methods=['GET'])
def get_ride_visualizations(digest, segment):
    try:
        url = get_visualization_url(digest, segment)
        status = 200
    except BaseException as e:
        print('Error: visualize - {}'.format(e))
        status = 400

    success = False
    if status == 200:
        message = 'SUCCESS'
        success = True
    else:
        message = 'FAILED'
    log_api_status('/visualize/{}/{}'.format(digest, segment), success, message, host='localhost')

    return redirect(url, code=302)


if __name__ == '__main__':
    # start flask app
    app.run(host="0.0.0.0", port=5000)
