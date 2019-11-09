import pika
import time
from PIL import Image
import io
import pickle
import socket
from utils.DataParser import GPXDataParser



def callback(ch, method, properties, body):
    md5, filename, file_data = pickle.loads(body)
    dataparser = GPXDataParser(file_data.decode('utf-8'))
    data_dict = dataparser.get_ride_data()
    print(data_dict)
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
