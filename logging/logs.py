import pika
import sys

mq_host = 'rabbitmq'

connection = pika.BlockingConnection(pika.ConnectionParameters(host=mq_host))
channel = connection.channel()

channel.exchange_declare(exchange='logs', exchange_type='topic')

result = channel.queue_declare('', exclusive=True)
queue_name = result.method.queue

# listen to any log message
channel.queue_bind(exchange='logs', queue=queue_name, routing_key='#')

print(' [*] Waiting for logs. To exit press CTRL+C')

def callback(ch, method, properties, body):
    print(" [x] %r: %r" % (method.routing_key, body))
    print()

channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
channel.start_consuming()
