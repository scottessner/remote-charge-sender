
import pika

connection = pika.BlockingConnection(pika.ConnectionParameters('192.168.40.10'))
channel = connection.channel()

# channel.exchange_declare(exchange='amq.fanout',
#                         type='fanout')

result = channel.queue_declare(exclusive=True)
queue_name = result.method.queue

channel.queue_bind(exchange='amq.fanout',
                   routing_key='battery',
                   queue=queue_name)


def callback(ch, method, properties, body):
    print('Received {0}'.format(body))

channel.basic_consume(callback,
                      queue=queue_name,
                      no_ack=True)

channel.start_consuming()