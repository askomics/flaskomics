#! /bin/bash

# Paths
dir_askomics=$(dirname "$0")
dir_venv="$dir_askomics/venv"
dir_node_modules="$dir_askomics/node_modules"
activate="$dir_venv/bin/activate"

# Check dependancies
python3 --version > /dev/null 2>&1 || { echo "python3 required but not installed. Abording." >&2; exit 1; }
npm -v > /dev/null 2>&1 || { echo "npm required but not installed. Abording." >&2; exit 1; }

# create python venv if not exists
if [[ ! -f $activate ]]; then
    echo "Building Python virtual environment ..."
    python3 -m venv venv
    echo "Sourcing Python virtual environment ..."
    source ${dir_venv}/bin/activate
    pip install --upgrade pip
else
    echo "Sourcing Python virtual environment ..."
    source ${dir_venv}/bin/activate
fi

trap 'kill 0' INT

# install python dependancies inside the virtual environment
echo "Installing Python dependancies inside the virtual environment ..."
pip install -e . &

# Install npm dependancies in node_modules
echo "Installing npm dependancies inside node_modules ..."
npm install &

wait

echo "Installation done!"
