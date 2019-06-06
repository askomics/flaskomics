#! /bin/bash

# Paths
dir_askomics=$(dirname "$0")
dir_venv="$dir_askomics/venv"
dir_node_modules="$dir_askomics/node_modules"
activate="$dir_venv/bin/activate"

error=0

function usage() {
    echo "Usage: $0"
}

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


# Lint JS
echo "Linting JS files ..."
${dir_node_modules}/.bin/eslint --config ${dir_askomics}/.eslintrc.yml "${dir_askomics}/askomics/react/src/**" && echo "OK" || exit 1

# Lint Python
echo "Linting Python files ..."
flake8 ${dir_askomics}/askomics ${dir_askomics}/tests --ignore=E501,W504 && echo "OK" || exit 1

# Test Python
pytest -q --disable-warnings && echo "OK" || exit 1
