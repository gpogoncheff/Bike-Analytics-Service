import pika
import time
from PIL import Image
import io
import pickle
import socket
from utils.DataParser import GPXDataParser
from utils.DataAnalyzer import DataAnalyzer
from utils.Datastore_utils import add_ride, get_ride_data, get_aggregate_statistics

def generate_visualizations(analyer, data):
    pass

def get_summary_statistics(analyzer, data):
    duration = analyzer.get_elapsed_time(data['time'])
    distance = analyzer.get_distance(data['coords'])
    _, _, climb, descend = analyzer.get_elevation_statistics(data['ele'])
    return duration, distance, climb, descend

def callback(ch, method, properties, body):
    digest, filename, file_data = pickle.loads(body)
    dataparser = GPXDataParser(file_data.decode('utf-8'))
    segments_data = dataparser.get_ride_data()
    analyzer = DataAnalyzer()
    for i, data in enumerate(segments_data):
        duration, distance, climb, descend = get_summary_statistics(analyzer, data)
        generate_visualizations(analyzer, data)

        try:
            add_ride(digest, i, duration, distance, climb, descend)
        except BaseException as e:
            print('Failed to update DB - {}'.format(e))

    #print('results')
    #print(get_aggregate_statistics())
    #print()

    ch.basic_ack(delivery_tag=method.delivery_tag)


if __name__ == '__main__':
    # Set up rabbitmq connections
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='work_route', durable=True)
    # Initialize logging channel
    log_channel = connection.channel()
    log_channel.exchange_declare(exchange='logs', exchange_type='topic')

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue='work_route', on_message_callback=callback)

    print('[*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()
