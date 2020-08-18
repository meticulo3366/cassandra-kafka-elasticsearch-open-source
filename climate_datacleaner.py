import json
import datetime
from kafka import KafkaConsumer
from kafka import KafkaProducer
import calendar

#if you want to run outside of docker, simply change bootstrap_servers="localhost:29092"

# Here we connect to the kafka cluster and grab just one record, all climate data is a giant data dump, we are converting into a stream
consumer = KafkaConsumer('climate',max_poll_records=1,bootstrap_servers="kafka:9092", group_id=None, auto_offset_reset="earliest")
# we will also be producing our records
producer = KafkaProducer(bootstrap_servers="kafka:9092", key_serializer=str.encode,value_serializer=lambda v: json.dumps(v).encode('utf-8'))
# create a simple array of calendar month names
months = [x for x in calendar.month_name if x]

for message in consumer:
    climate = json.loads(message.value)
    for city in climate:
        # create empty object class
        record = {'city':'','country':'','month':'','low':'','dry':'','snow':'','rainfall':''}

        record['city'] = city['city']
        record['country'] = city['country']

        i = 0
        for month in months:
            record['month']    = month
            record['high']     = city['monthlyAvg'][i]['high']
            record['low']      = city['monthlyAvg'][i]['low']
            record['dry']      = city['monthlyAvg'][i]['dryDays']
            record['snow']     = city['monthlyAvg'][i]['snowDays']
            record['rainfall'] = city['monthlyAvg'][i]['rainfall']
            i = i + 1
            print(record)
            # send our records to a new topic called climateclean
            producer.send('climateclean', key=record['city'], value=record ) 

