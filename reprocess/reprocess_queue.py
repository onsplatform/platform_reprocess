import pika
import json


class ReprocessQueue():
    def __init__(self, queue, solution, settings):
        self.queue = queue + '_' + solution.lower()
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=settings['host']))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=self.queue, durable=True)

    def enqueue(self, id, event):
        self.channel.basic_publish(exchange='',
                                   routing_key=self.queue,
                                   body=json.dumps(event),
                                   properties=pika.BasicProperties(
                                       delivery_mode=2,  # make message persistent
                                   ))

    def check_next_message(self):
        return self.channel.basic_get(queue=self.queue, auto_ack=False)

    def dequeue(self):
        return self.channel.basic_get(queue=self.queue, auto_ack=True)

    def start_consuming(self):
        self.channel.start_consuming()

    def close(self):
        self.connection.close()
