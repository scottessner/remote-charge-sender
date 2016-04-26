import pika

connection = pika.BlockingConnection(pika.ConnectionParameters('192.168.40.10'))
channel = connection.channel()

channel.queue_declare(queue='batt')

while True:
    message = input()
    channel.basic_publish(exchange='amq.fanout',
                          routing_key='battery',
                          body=message
                          )
connection.close()
