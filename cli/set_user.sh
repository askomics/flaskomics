#! /bin/bash

# Create user (once) if CREATE_USER == true
first_name=$(if [ -z ${USER_FIRST_NAME} ]; then echo "Ad"; else echo "${USER_FIRST_NAME}"; fi)
last_name=$(if [ -z ${USER_LAST_NAME} ]; then echo "Min"; else echo "${USER_LAST_NAME}"; fi)
username=$(if [ -z ${USER_USERNAME} ]; then echo "admin"; else echo "${USER_USERNAME}"; fi)
user_password=$(if [ -z ${USER_PASSWORD} ]; then echo "admin"; else echo "${USER_PASSWORD}"; fi)
email=$(if [ -z ${USER_EMAIL} ]; then echo "admin@example.org"; else echo "${USER_EMAIL}"; fi)
api_key=$(if [ -z ${USER_APIKEY} ]; then echo "admin"; else echo "${USER_APIKEY}"; fi)

if [[ ! -z ${CREATE_USER} ]]; then
    if [[ ${CREATE_USER} == "true" ]]; then
        # Create default user
        galaxy_args=""
        if [[ ! -z ${GALAXY_API_KEY} ]]; then
            if [[ ! -z ${GALAXY_URL} ]]; then
                galaxy_args="-g ${GALAXY_URL} -gk ${GALAXY_API_KEY}"
            fi
        fi
        python3 cli/add_user.py -c config/askomics.ini -f ${first_name} -l ${last_name} -u ${username} -p ${user_password} -e ${email} -k ${api_key} ${galaxy_args}
    fi
fi
