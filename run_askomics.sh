#! /bin/bash

# Paths
dir_askomics=$(dirname "$0")
dir_venv="$dir_askomics/venv"
dir_node_modules="$dir_askomics/node_modules"
activate="$dir_venv/bin/activate"

error=0

function usage() {
    echo "Usage: $0 (-d { dev | prod })"
    echo "    -d     deployment mode (default: production)"
}

while getopts "hd:" option; do
    case $option in
        h)
            usage
            exit 0
        ;;

        d)
            depmode=$OPTARG
        ;;
    esac
done

case $depmode in
    prod|production|"")
        flask_depmod="production"
        flask_command="gunicorn -b 0.0.0.0:5000 app"
    ;;
    dev|development)
        flask_depmod="development"
        flask_command="flask run --host=0.0.0.0"
        npm run dev &
    ;;
    *)
        echo "-d $depmode: wrong deployment mode"
        usage
        exit 1
esac

# Exports
export FLASK_ENV=$flask_depmod
export FLASK_APP="app"

echo "Removing python cache ..."
find . | grep -E "(__pycache__|\.pyc|\.pyo$)" | xargs rm -rf

if [[ -f $activate ]]; then
    echo "Sourcing Python virtual environment ..."
    source ${dir_venv}/bin/activate
else
    echo "No virtual environment found. Run install.sh first."
    error=1
fi

if [[ ! -d $dir_node_modules ]]; then
    echo "No node_modules directory found. Run install.sh first."
    error=1
fi

if [[ ! -f $dir_askomics/askomics/static/js/askomics.js ]]; then
    echo "Javascript not built. Run build.sh first."
    error=1
fi

if [[ $error > 0 ]]; then
    exit 1
fi

# Create config file
config_template_path="$dir_askomics/config/askomics.ini.template"
config_path="$dir_askomics/config/askomics.ini"
if [[ ! -f $config_path ]]; then
    cp $config_template_path $config_path
fi

# Convert env to ini entry
printenv | egrep "ASKO_" | while read setting
do
    section=$(echo $setting | egrep -o "^ASKO[^=]+" | sed 's/^.\{5\}//g' | cut -d "_" -f 1)
    key=$(echo $setting | egrep -o "^ASKO[^=]+" | sed 's/^.\{5\}//g' | sed "s/$section\_//g")
    value=$(echo $setting | egrep -o "=.*$" | sed 's/^=//g')
    # crudini --set ${config_path} "${section}" "${key}" "${value}"
    python3 config_updater.py -p $config_path -s "${section}" -k "${key}" -v "${value}"
    $cmd

done

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
        python3 /askomics/cli/add_user.py -c /askomics/config/askomics.ini -f ${first_name} -l ${last_name} -u ${username} -p ${user_password} -e ${email} -k ${api_key} ${galaxy_args}
    fi
fi

echo "Starting AskOmics ..."
$flask_command
