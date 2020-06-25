# cassandra-kafka-elasticsearch-open-source
a open source project to demonstrate a data pipeline from REST API all the way to elasticsearch through kafka connectors and some kind of data manipulation

## Inspiration
We needed a data pipeline to demonstrate the functionality of cassandra / kafka / elasticsearch


## Pre-requisites
* Set up and install Docker
* Download the kafka connectors 
* see [ReadMe](./README.md) if you are facing any challenges



## Open another terminal and Enable the connectors 
```
curl -X POST -H 'Accept: application/json'    -H 'Content-Type: application/json'   http://localhost:8083/connectors -d @connector-configs/current-datetime.json
curl -X POST -H 'Accept: application/json'    -H 'Content-Type: application/json'   http://localhost:8083/connectors -d @connector-configs/utcelk.json
curl -X POST -H 'Accept: application/json'    -H 'Content-Type: application/json'   http://localhost:8083/connectors -d @connector-configs/utccassandra.json
```

## Open another terminal to validate the connectors
verify the rest connector is ingesting data 
```
docker exec -it cassandra-kafka-elasticsearch-open-source_connect_1 bash -c   "kafka-console-consumer --bootstrap-server kafka:9092   --topic current-datetime --from-beginning"
```

#### Validate elasticsearch has ingested the data
* input

	`curl http://127.0.0.1:9200/current-datetime/_search/?size=1000&pretty=1`

* validate to ensure you have some json output

*Check the console*
`{"took":8,"timed_out":false,"_shards":{"total":1,"successful":1,"skipped":0,"failed":0},"hits":{"total":{"value":29,"relation":"eq"},"max_score":1.0,"hits":[{"_index":"current-datetime","_type":"current-datetime","_id":"current-datetime-0-0","_score":1.0,"_source":{"dayOfTheWeek":"Tuesday","currentDateTime":"2020-04-14T01:03Z","currentFileTime":132312998369757549}},{"_index":"current-datetime","_type":"current-datetime","_id":"current-datetime-0-1","_score":1.0,"_source":{"dayOfTheWeek":"Tuesday","currentDateTime":"2020-04-14T01:04Z","currentFileTime":132312998970689266}},{"_index":"current-datetime","_type":"current-datetime","_id":"current-datetime-0-2","_score":1.0,"_source":{"dayOfTheWeek":"Tuesday","currentDateTime":"2020-04-14T01:05Z","currentFileTime":132312999571657054}},{"_index":"current-datetime","_type":}]}}`

#### open another terminal and Validate Cassandra has ingested the data
* input
```
docker exec -it cassandra-kafka-elasticsearch-open-source_cassandra_1 bash

cqlsh

select * from test.clock;
```
* validate

 currentfiletime    | currentdatetime   | dayoftheweek
--------------------+-------------------+--------------
 132312998369757549 | 2020-04-14T01:03Z |      Tuesday
 132312999571657054 | 2020-04-14T01:05Z |      Tuesday
 132312998970689266 | 2020-04-14T01:04Z |      Tuesday


## Understanding Data Flows - Time Clock syncing

![alt text](./diagram.jpg "Logo Title Text 1")

#### Kafka REST Connector
look at the configuration for the rest connector [link to connector source code](https://github.com/llofberg/kafka-connect-rest)

rest connector creates its own topic

```
{
    "name": "source_rest_current-datetime",
    "config": {
      "key.converter":"org.apache.kafka.connect.storage.StringConverter",
      "value.converter":"org.apache.kafka.connect.storage.StringConverter",
      "connector.class": "com.tm.kafka.connect.rest.RestSourceConnector",
      "tasks.max": "1",
      "rest.source.poll.interval.ms": "60000",
      "rest.source.method": "GET",
      "rest.source.url": "http://worldclockapi.com/api/json/utc/now",
      "rest.source.headers": "Content-Type:application/json,Accept:application/json",
      "rest.source.topic.selector": "com.tm.kafka.connect.rest.selector.SimpleTopicSelector",
      "rest.source.destination.topics": "current-datetime"
    }
}
```

#### Kafka ElasticSearch Connector
look at the configuration for the elk connector
[link to connector source code](https://github.com/lensesio/stream-reactor/tree/master/kafka-connect-elastic6)

```
{
	"name": "elk",
	"config":{
		"connector.class":"com.datamountaineer.streamreactor.connect.elastic6.ElasticSinkConnector",
		"tasks.max":"1",
		"topics":"current-datetime",
		"connect.elastic.url":"elasticsearch:9200",
		"connect.elastic.use.http":"http",
		"connect.elastic.kcql":"INSERT INTO current-datetime SELECT dayOfTheWeek,currentDateTime,currentFileTime FROM current-datetime",
		"connect.progress.enabled":"true"
	}
}
```

#### Kafka Cassandra Connector
* look at the configuration for the cassandra connector
[link to connector source code](https://github.com/lensesio/stream-reactor/tree/master/kafka-connect-cassandra)

    ```
{
  "name": "utccassandra",
  "config": {
    "tasks.max": "1",
    "connector.class": "com.datamountaineer.streamreactor.connect.cassandra.sink.CassandraSinkConnector",
    "connect.cassandra.contact.points":"cassandra",
    "connect.cassandra.port":"9042",
    "connect.cassandra.consistency.level": "LOCAL_ONE",
    "connect.cassandra.key.space": "test",
    "connect.cassandra.kcql": "INSERT INTO clock SELECT dayOfTheWeek,currentDateTime,currentFileTime FROM current-datetime",
    "topics": "current-datetime"
  }
}
```

* look at the boot up process for cassandra

    ```
cat >/import.cql <<EOF
DROP keyspace test;
CREATE keyspace test with replication = {'class':'SimpleStrategy', 'replication_factor' : 1} AND durable_writes = true;
CREATE TABLE test.clock ( 
	dayOfTheWeek text,
	currentDateTime text,
	currentFileTime timestamp,
	PRIMARY KEY (currentFileTime)
);
EOF
```

* look at docker compose 
    
    ```
      cassandra:
    image: cassandra:3.0.20
    volumes:
      - "./cassandra-init.sh:/cassandra-init.sh"
    command: "sh /cassandra-init.sh"
    ports:
      - "9042:9042"
    links:
      - connect
    ```

## look at the cassandra boot script

```
until cqlsh -f /import.cql; do
  echo "cqlsh: Cassandra is unavailable to initialize - will retry later"
  sleep 2
done &

exec /docker-entrypoint.sh "$@"
```
  * docker-compose program entry

```
  cassandra:
    image: cassandra:3.0.20
    volumes:
      - "./cassandra-init.sh:/cassandra-init.sh"
    command: "sh /cassandra-init.sh"
    ports:
      - "9042:9042"
    links:
      - connect
```

## Do some data exploration with kibana
1. [Navigate to Kibana](http://localhost:5601/app/kibana#/management/kibana/index_pattern?_g=())

![alt text](./kibana.png "Logo Title Text 1")
![alt text](./timeseries.png "Logo Title Text 1")
