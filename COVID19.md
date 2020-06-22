# COVID19 Data Sets and Visualization

## Inspiration
We needed a data pipeline to demonstrate the functionality of  kafka and elasticsearch and proper data science workflows

## Pre-requisites
* Set up and install Docker
* Download the kafka connectors 
* see [ReadMe](./README.md) if you are facing any challenges

#### COVID19 Data
```
curl -X POST -H 'Accept: application/json'    -H 'Content-Type: application/json'   http://localhost:8083/connectors -d @connector-configs/covid19restALL.json
```

#### Stock Trading Volatility VIX Data
```
curl -X POST -H 'Accept: application/json'    -H 'Content-Type: application/json'   http://localhost:8083/connectors -d @connector-configs/vixrest.json
```

#### Run the python data cleaner

Follow instructions below

1. Set up your python environment (requires python 3)

```
pip3 install kafka-python
pip3 install snappy
pip3 install python-snappy
```

2. Run the code to clean the data

```
python3 covid19_datacleaner.py
```

3. Validate that you have cleaned the data successfully
```
docker exec -it cassandra-kafka-elasticsearch-open-source_connect_1 bash -c   "kafka-console-consumer --bootstrap-server kafka:9092   --topic covid19US  --from-beginning"
```

#### Send the data to elastic search
```
curl -X POST -H 'Accept: application/json'    -H 'Content-Type: application/json'   http://localhost:8083/connectors -d @connector-configs/covid19USelk.json
```

#### Validate elasticsearch has ingested the data

```
curl http://127.0.0.1:9200/covid19us/_search/?size=1000&pretty=1
```

## Market Volatility: Let's add some more data sources

#### adding vix data

```
curl -X POST -H 'Accept: application/json'    -H 'Content-Type: application/json'   http://localhost:8083/connectors -d @connector-configs/vixrest.json
```

#### Parse the VIX data and insert into a topic

```
python3 vix_datacleaner.py
```

#### Validate the data matches what we expect

```
docker exec -it cassandra-kafka-elasticsearch-open-source_connect_1 bash -c   "kafka-console-consumer --bootstrap-server kafka:9092   --topic vixClean  --from-beginning"
```

#### Turn on the connector and send to Elastic Search

```
curl -X POST -H 'Accept: application/json'    -H 'Content-Type: application/json'   http://localhost:8083/connectors -d @connector-configs/vixelk.json
```

## examine the data in elastic search


# Trouble Shooting Connectors

```
curl -X DELETE http://localhost:8083/connectors/<connector-name>
```

docker-compose up --force-recreate -V --remove-orphans --always-recreate-deps


