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

# You may add some other conditionals that fits your stuation here
until cqlsh -f /import.cql; do
  echo "cqlsh: Cassandra is unavailable to initialize - will retry later"
  sleep 2
done &

exec /docker-entrypoint.sh "$@"