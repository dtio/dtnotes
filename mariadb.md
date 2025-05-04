
Replication configuration

# applies to master:
server-id=1
log-bin=mysql-bin
binlog-do-db=exampledb

# applies to slave:
replicate-do-db=exampledb
relay-log=mysql-relay-bin
relay-log-index=mysql-relay-bin.index
read-only=1

# applies to slave:
replicate_ignore_table=exampledb.table1
replicate_ignore_table=exampledb.table2
replicate_ignore_table=exampledb.table3
server-id=2 # on slave

# Run on SLAVE
CHANGE MASTER TO
MASTER_HOST='galera-mariadb-galera',
MASTER_USER='ftrepl',
MASTER_PASSWORD='replpass',
MASTER_PORT=3306,
MASTER_LOG_FILE='mysql-bin.000004',
MASTER_LOG_POS=1032823,
MASTER_CONNECT_RETRY=10;