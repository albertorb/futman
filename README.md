futman
======

Football manager web information system

#start postgresql
pg_ctl -D /usr/local/var/postgres -l /usr/local/var/postgres/server.log start

# configure database

createuser -s -r username
psql
ALTER USER username WITH PASSWORD password
createdb dbname
