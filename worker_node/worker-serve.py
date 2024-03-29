import pika
import time
from PIL import Image
import io
import pickle
import socket
from utils.DataParser import GPXDataParser
from utils.DataAnalyzer import DataAnalyzer
import utils.Datastore as datastore
from utils.CloudStorage import upload_visualization, upload_file

mq_host = 'rabbitmq'

def log_work(work_description, success):
    # log the api that was called and the result of the api call
    try:
        log_connection = pika.BlockingConnection(pika.ConnectionParameters(host=mq_host))
        log_channel = log_connection.channel()
        log_channel.exchange_declare(exchange='logs', exchange_type='topic')

        log_channel.basic_publish(
            exchange='logs',
            routing_key='{}.worker.info'.format(socket.gethostname()),
            body='{}'.format(work_description)
        )
        if not success:
            log_channel.basic_publish(
                exchange='logs',
                routing_key='{}.worker.debug'.format(socket.gethostname()),
                body='{} - FAILED'.format(work_description)
            )
    except BaseException as e:
        print('Failed to log worker message - {}'.format(e))

    if log_connection is not None:
        log_connection.close()


def get_visualization(analyzer, data, digest, segment):
    # return url for the visualization
    buff = analyzer.generate_data_visualizations(data['time'], data['power'], data['ele'])
    url = upload_visualization(digest, segment, buff)
    buff.close()
    if url == '':
        log_work('Failed to save visualization for {}'.format(digest), success=False)
    else:
        log_work('Saved visualization for {} at {}'.format(digest, url), success=True)
    return url

def get_summary_statistics(analyzer, data):
    duration = analyzer.get_elapsed_time(data['time'])
    distance = analyzer.get_distance(data['coords'])
    _, _, climb, descend = analyzer.get_elevation_statistics(data['ele'])
    return duration, distance, climb, descend


def callback(ch, method, properties, body):
    is_valid_data = False

    try:
        digest, filename, file_data = pickle.loads(body)
        dataparser = GPXDataParser(file_data.decode('utf-8'))
        segments_data = dataparser.get_ride_data()
        analyzer = DataAnalyzer()
        is_valid_data = True
    except:
        print('Uploaded data file does not contain valid data')

    if is_valid_data:
        for i, data in enumerate(segments_data):
            duration, distance, climb, descend = get_summary_statistics(analyzer, data)
            url = get_visualization(analyzer, data, digest, i)
            print('Ride data visualization available at: {}'.format(url))

            try:
                datastore.add_ride(digest, i, duration, distance, climb, descend)
                log_work('Added data from {} to Datastore DB'.format(digest), success=True)
            except BaseException as e:
                print('Failed to update Database - {}'.format(e))
                log_work('Failed to add data from {} to Datastore DB'.format(digest), success=False)

        upload_file(digest, file_data.decode('utf-8'))
        log_work('Uploaded data file with digest {} to Cloud Storage'.format(digest), success=True)

    ch.basic_ack(delivery_tag=method.delivery_tag)


if __name__ == '__main__':
    # Set up rabbitmq connections
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=mq_host))
    channel = connection.channel()
    channel.queue_declare(queue='work_route', durable=True)
    # Initialize logging channel
    log_channel = connection.channel()
    log_channel.exchange_declare(exchange='logs', exchange_type='topic')

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue='work_route', on_message_callback=callback)

    print('[*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()
