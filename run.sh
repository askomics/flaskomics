#! /bin/bash

# Paths
dir_askomics=$(dirname "$0")
dir_venv="$dir_askomics/venv"
dir_node_modules="$dir_askomics/node_modules"
activate="$dir_venv/bin/activate"

error=0

# Exports
export FLASK_ENV=development
export FLASK_APP=$dir_askomics/askomics

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

# Run
npm run dev &
flask run
