## Alternative

It is also possible to hook directly into the *neutron* topic exchange in
RabbitMQ, this should permit receiving notifications of Neutron changes even
if ML2 is not used.

Sample code:

    import amqp
    import logging
    import json
    import pprint
    
    LOG = logging.getLogger(__name__)
    
    logging.basicConfig(level=logging.DEBUG)
    
    def callback(msg):
        print
        print '--- message'
        msg = json.loads(msg.body)
        oslo_message = json.loads(msg['oslo.message'])
        pprint.pprint(oslo_message)
    
    conn = amqp.connection.Connection(
        userid='stackrabbit',
        password='supersecret'
    )
    channel = conn.channel()
    channel.exchange_declare(
        'neutron',
        'topic',
        durable=False,
        auto_delete=False
    )
    q = channel.queue_declare(
        exclusive=False
    )
    
    channel.queue_bind(
        queue=q.queue,
        exchange='neutron',
        routing_key='#'
    )
    channel.basic_consume(
        callback=callback,
        no_ack=True,
        exclusive=True
    )
    
    while True:
        conn.drain_events()
