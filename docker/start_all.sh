#! /bin/bash

################################################
#                                              #
#   Run AskOmics inside the Docker container   #
#                                              #
################################################

cd /askomics

first_name=$(if [ -z ${USER_FIRST_NAME} ]; then echo "Ad"; else echo "${USER_FIRST_NAME}"; fi)
last_name=$(if [ -z ${USER_LAST_NAME} ]; then echo "Min"; else echo "${USER_LAST_NAME}"; fi)
username=$(if [ -z ${USER_USERNAME} ]; then echo "admin"; else echo "${USER_USERNAME}"; fi)
user_password=$(if [ -z ${USER_PASSWORD} ]; then echo "admin"; else echo "${USER_PASSWORD}"; fi)
email=$(if [ -z ${USER_EMAIL} ]; then echo "admin@example.org"; else echo "${USER_EMAIL}"; fi)
api_key=$(if [ -z ${USER_APIKEY} ]; then echo "admin"; else echo "${USER_APIKEY}"; fi)

# Start Redis
nohup /usr/bin/redis-server &> /var/log/redis-server.log &

# Start Virtuoso
nohup /virtuoso/virtuoso.sh &> /var/log/virtuoso.log &

# Start Corese
nohup sh /corese/start.sh &> /var/log/corese.log &

# Activate python venv
source /askomics/venv/bin/activate

if [ $DEPMODE = "dev" ]; then
    # Rebuild JS with dev mode
    npm run dev &
fi

# Wait for virtuoso to be up
while ! wget -O /dev/null http://localhost:8890/conductor/; do
    sleep 1s
done

# Start AskOmics
/askomics/run_askomics.sh -d ${DEPMODE} &> /var/log/askomics.log &

# Wait for config file to be available
while [[ ! -f /askomics/config/askomics.ini ]]; do
    sleep 1s
done

# Start Celery
/askomics/run_celery.sh -d ${DEPMODE} -c ${MAX_CELERY_QUEUE} &> /var/log/celery.log &

# Create user and upload files if CREATE_USER == true
if [[ ! -z ${CREATE_USER} ]]; then
    if [[ ${CREATE_USER} == "true" ]]; then
        # Create default user
        galaxy_args=""
        if [[ ! -z ${GALAXY_API_KEY} ]]; then
            if [[ ! -z ${GALAXY_URL} ]]; then
                galaxy_args="-g ${GALAXY_URL} -gk ${GALAXY_API_KEY}"
            fi
        fi

        python3 /askomics/cli/add_user.py -c /askomics/config/askomics.ini -f ${first_name} -l ${last_name} -u ${username} -p ${user_password} -e ${email} -k ${api_key} ${galaxy_args}

        # Upload file in /import
        if [[ -d /import ]]; then
            python3 /askomics/cli/upload_files.py -c /askomics/config/askomics.ini -d /import -k ${api_key}
        fi
    fi
fi

tail -f /var/log/askomics.log & tail -f /var/log/celery.log
