import json
import datetime
from kafka import KafkaConsumer
from kafka import KafkaProducer
# Here we connect to the kafka cluster and grab just one record, all vix data is a giant data dump, we are converting into a stream
consumer = KafkaConsumer('vix',max_poll_records=1,bootstrap_servers="localhost:29092", group_id=None, auto_offset_reset="earliest")
# we will also be producing our records
producer = KafkaProducer(bootstrap_servers="localhost:29092", key_serializer=str.encode,value_serializer=lambda v: json.dumps(v).encode('utf-8'))
now = datetime.datetime.now()
for message in consumer:
    vix = json.loads(message.value)
    for i in vix:
        #Let's filter out data we don't need prior to 2020
        record_date = datetime.datetime.strptime(i['Date'], '%Y-%m-%d')
        if record_date.year == now.year:
            #lets clean up those white spaces as this will cause issues with our queries
            i["vix"] = i.pop("VIX High")
            i["vix_open"] = i.pop("VIX Open")
            i["vix_close"] = i.pop("VIX Close")
            i["vix_low"] = i.pop("VIX Low")
            i["date"] = i.pop("Date")
            producer.send('vixClean', key=i['date'], value=i ) 
            print(i)
