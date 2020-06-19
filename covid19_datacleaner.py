import json
from kafka import KafkaConsumer
from kafka import KafkaProducer
# Here we connect to the kafka cluster and grab just one record, all covid data is a giant data dump, we are converting into a stream
consumer = KafkaConsumer('covid19Global',max_poll_records=1,bootstrap_servers="localhost:29092", group_id=None, auto_offset_reset="earliest")
# we will also be producing our records
producer = KafkaProducer(bootstrap_servers="localhost:29092", key_serializer=str.encode,value_serializer=lambda v: json.dumps(v).encode('utf-8'))
for message in consumer:
    covid = json.loads(message.value)
    for i in covid["US"]:
    	#we are sending our records to a new topic called covid19US
        producer.send('covid19US', key=i['date'], value=i ) 
        print(i)
