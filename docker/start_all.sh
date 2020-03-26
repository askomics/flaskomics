#! /bin/bash

################################################
#                                              #
#   Run AskOmics inside the Docker container   #
#                                              #
################################################

cd /askomics

# Start Redis
nohup /usr/bin/redis-server &> /var/log/redis-server.log &

# Start Virtuoso
nohup /virtuoso/virtuoso.sh &> /var/log/virtuoso.log &

# Start Corese
nohup sh /corese/start.sh &> /var/log/corese.log &

# Wait for virtuoso to be up
while ! wget -O /dev/null http://localhost:8890/conductor/; do
    sleep 1s
done

# Start AskOmics
nohup make serve-askomics &> /var/log/askomics.log &

# Wait for config file to be available
while [[ ! -f /askomics/config/askomics.ini ]]; do
    sleep 1s
done

# Start Celery
nohup make serve-celery &> /var/log/celery.log &

tail -f /var/log/askomics.log & tail -f /var/log/celery.log
