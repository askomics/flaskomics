#! /bin/bash

# Paths
dir_askomics=$(dirname "$0")
dir_venv="$dir_askomics/venv"

# Exports
export FLASK_ENV=development
export FLASK_APP=askomics/askomics.py

# Run
source ${dir_venv}/bin/activate
flask run
