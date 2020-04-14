# cassandra-kafka-elasticsearch-open-source
a open source project to demonstrate a data pipeline from REST API all the way to elasticsearch through kafka connectors and some kind of data manipulation

## Inspiration
We needed a data pipeline to demonstrate the functionality of cassandra / kafka / elasticsearch

## Pre-requisites
* Set up and install Docker
* Download the kafka connectors 

	```
	cd jars/
	wget https://cassandra-kafka-elasticsearch-open-source.s3-us-west-1.amazonaws.com/kafka-connect-rest-plugin-1.0.3-shaded.jar
	wget https://cassandra-kafka-elasticsearch-open-source.s3-us-west-1.amazonaws.com/kafka-connect-transform-add-headers-1.0.3-shaded.jar
	wget https://cassandra-kafka-elasticsearch-open-source.s3-us-west-1.amazonaws.com/kafka-connect-transform-from-json-plugin-1.0.3-shaded.jar
	wget https://cassandra-kafka-elasticsearch-open-source.s3-us-west-1.amazonaws.com/kafka-connect-transform-velocity-eval-1.0.3-shaded.jar
	wget https://github.com/lensesio/stream-reactor/releases/download/1.2.3/kafka-connect-elastic6-1.2.3-2.1.0-all.tar.gz
	wget https://cassandra-kafka-elasticsearch-open-source.s3-us-west-1.amazonaws.com/kafka-connect-cassandra-1.2.3-2.1.0-all.jar
	```

## Deploy the docker environment


## Enable the connectors
1. `curl -X POST -H 'Accept: application/json'    -H 'Content-Type: application/json'   http://localhost:8083/connectors -d @connector-configs/current-datetime.json`
2. `curl -X POST -H 'Accept: application/json'    -H 'Content-Type: application/json'   http://localhost:8083/connectors -d @connector-configs/utcelk.json`
3. `curl -X POST -H 'Accept: application/json'    -H 'Content-Type: application/json'   http://localhost:8083/connectors -d @connector-configs/utccassandra.json`

verify the rest connector is ingesting data 
`docker exec -it spring_connect_1 bash -c   "kafka-console-consumer --bootstrap-server kafka:9092   --topic current-datetime --from-beginning"`

#### Validate Cassandra has ingested the data
* input
`docker exec -it cassandra-kafka-elasticsearch-open-source_cassandra_1 bash`
`select * from test.clock;`
* validate

 currentfiletime    | currentdatetime   | dayoftheweek
--------------------+-------------------+--------------
 132312998369757549 | 2020-04-14T01:03Z |      Tuesday
 132312999571657054 | 2020-04-14T01:05Z |      Tuesday
 132312998970689266 | 2020-04-14T01:04Z |      Tuesday


## Understanding Data Flows - Time Clock syncing
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
look at the configuration for the rest connector
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
