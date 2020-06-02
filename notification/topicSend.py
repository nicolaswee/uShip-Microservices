import pika
import json
url = "amqp://fvygipjl:6tWNAyMOkLyoZHHWx5fuYMmbbgLhM5qv@vulture.rmq.cloudamqp.com/fvygipjl"
params = pika.URLParameters(url)
connection = pika.BlockingConnection(params)
channel = connection.channel()
exchangename="uship"
channel.exchange_declare(exchange=exchangename, exchange_type='topic')

# body = {"subject": "pending", "content":  "CONTENT", "id": "jtRqjP", 'content': "adsfasdfasdf", "to": "ushipnotification@gmail.com", "admin": True}

# body = json.dumps(body, default=str)

# channel.queue_declare(queue='notification', durable=True) # make sure the queue used by Shipping exist and durable
# channel.queue_bind(exchange=exchangename, queue='notification', routing_key='*.notification') # make sure the queue is bound to the exchange
# channel.basic_publish(exchange=exchangename, routing_key="pending.notification", body=body, properties=pika.BasicProperties(delivery_mode = 2))

body = {"subject": "pending", "id": "zUawoN", 'content': "dsafsdaf", "to": "danialshahz.2018@sis.smu.edu.sg", "admin": True}
body = json.dumps(body, default=str)
channel.queue_declare(queue='notification', durable=True)
channel.queue_bind(exchange=exchangename, queue='notification', routing_key='*.notification')
channel.basic_publish(exchange=exchangename, routing_key="pending.notification", body=body, properties=pika.BasicProperties(delivery_mode = 2))

print("Order sent for consumption.")