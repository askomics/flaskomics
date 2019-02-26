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
        npm_depmode="prod"
        flask_command="gunicorn -b localhost:5000 app"
    ;;
    dev|development)
        flask_depmod="development"
        npm_depmode="dev"
        flask_command="flask run"
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

if [[ $error > 0 ]]; then
    exit 1
fi

# Create config file
config_template_path="$dir_askomics/config/askomics.ini.template"
config_path="$dir_askomics/config/askomics.ini"
if [[ ! -f $config_path ]]; then
    cp $config_template_path $config_path
fi

trap 'kill 0' INT

# Run
echo "Building JS ..."
npm run $npm_depmode &
echo "Starting celery ..."
celery -A askomics.tasks.celery worker -l info &

echo "Starting server ..."
$flask_command &

wait
