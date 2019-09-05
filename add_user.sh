#! /bin/bash

#####################################################
#                                                   #
#       Add a user into the AskOmics database       #
#                                                   #
#####################################################

data_directory=$(if [ -z ${ASKO_askomics_data_directory} ]; then echo "/tmp/flaskomics"; else echo "${ASKO_askomics_data_directory}"; fi)
database_path=$(if [ -z ${ASKO_askomics_database_path} ]; then echo "/tmp/flaskomics/database.db"; else echo "${ASKO_askomics_database_path}"; fi)

# Create data directory
mkdir -p ${data_directory}

# Insert a user in the database only if the database don't exist
if [[ ! -f ${database_path} ]]; then
    first_name=$(if [ -z ${USER_FIRST_NAME} ]; then echo "Ad"; else echo "${USER_FIRST_NAME}"; fi)
    last_name=$(if [ -z ${USER_LAST_NAME} ]; then echo "Min"; else echo "${USER_LAST_NAME}"; fi)
    username=$(if [ -z ${USERNAME} ]; then echo "admin"; else echo "${USERNAME}"; fi)
    user_password=$(if [ -z ${USER_PASSWORD} ]; then echo "admin"; else echo "${USER_PASSWORD}"; fi)
    email=$(if [ -z ${USER_EMAIL} ]; then echo "admin@example.org"; else echo "${USERNAME}"; fi)
    api_key=$(if [ -z ${USER_APIKEY} ]; then echo "admin"; else echo "${USER_APIKEY}"; fi)

    password_salt=$(if [ -z ${ASKO_askomics_password_salt} ]; then echo "4sk0mIcs"; else echo "${ASKO_askomics_password_salt}"; fi)
    user_salt=$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 20 | head -n 1)

    salted_password=$(echo ${password_salt}${user_password}${user_salt})
    hash_password=$(python3 -c "import hashlib; print(hashlib.sha512('${salted_password}'.encode('utf8')).hexdigest())")

    # Create database and user table
    sqlite3 ${database_path} "CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY AUTOINCREMENT, ldap boolean, fname text, lname text, username text, email text, password text, salt text, apikey text, admin boolean, blocked boolean)"
    # Insert the user
    sqlite3 ${database_path} "INSERT INTO users VALUES(NULL, 'false', '${first_name}', '${last_name}', '${username}', '${email}', '${hash_password}', '${user_salt}', '${api_key}', 1, 0)"
    # get user id
    user_id=$(sqlite3 ${database_path} "select user_id from users where username='${username}';")

    # Create the user data directory
    mkdir -p ${data_directory}/${user_id}_${username}/results
    mkdir -p ${data_directory}/${user_id}_${username}/ttl
    mkdir -p ${data_directory}/${user_id}_${username}/upload

    #TODO: link the eventualy galaxy uploaded dataset into the upload directory

    # If GALAXY_API_KEY and GALAXY_URL are set, insert the galaxy account in the database for the newly created user
    if [[ ! -z ${GALAXY_API_KEY} ]]; then
        if [[ ! -z ${GALAXY_URL} ]]; then
            # create galaxy database
            sqlite3 ${database_path} "CREATE TABLE IF NOT EXISTS galaxy_accounts (galaxy_id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, url text, apikey text, FOREIGN KEY(user_id) REFERENCES users(user_id))"
            # Insert Galaxy account
            sqlite3 ${database_path} "INSERT INTO galaxy_accounts VALUES(NULL, '${user_id}', '${GALAXY_URL}', '${GALAXY_API_KEY}');"
        fi
    fi
fi
