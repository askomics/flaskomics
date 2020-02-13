#! /bin/bash

#####################################################
#                                                   #
#        Install python and npm dependancies        #
#                                                   #
#####################################################

# Paths
dir_askomics=$(dirname "$0")
dir_venv="$dir_askomics/venv"
dir_node_modules="$dir_askomics/node_modules"
activate="$dir_venv/bin/activate"

function usage() {
    echo "Usage: $0 (-d { dev | prod }) (-i { js | python })"
    echo "    -i     ignore install of python or js"
    echo "    -d     deployment mode (default: production)"
}

while getopts "hi:d:" option; do
    case $option in
        h)
            usage
            exit 0
        ;;

        d)
            depmode=$OPTARG
        ;;

        i)
            ignored=$OPTARG
        ;;
    esac
done

case $depmode in
    prod|production|"")
        pipenv_opt=""
    ;;
    dev|development)
        pipenv_opt="--dev"
    ;;
    *)
        echo "-d $depmode: wrong deployment mode"
        usage
        exit 1
esac

if [[ $ignored != "python" ]]; then
    python3 --version > /dev/null 2>&1 || { echo "python3 required but not installed. Abording." >&2; exit 1; }
    # create python venv if not exists
    if [[ ! -f $activate ]]; then
        echo "Building Python virtual environment ..."
        python3 -m venv venv
        echo "Sourcing Python virtual environment ..."
        source ${dir_venv}/bin/activate
        pip3 install --upgrade pip
    else
        echo "Sourcing Python virtual environment ..."
        source ${dir_venv}/bin/activate
    fi

    # install python dependancies inside the virtual environment
    echo "Installing Python dependancies inside the virtual environment ..."
    pip3 install -e .
    pipenv install ${pipenv_opt}
fi

if [[ $ignored != "js" ]]; then
    # Check dependancies
    npm -v > /dev/null 2>&1 || { echo "npm required but not installed. Abording." >&2; exit 1; }
    # Install npm dependancies in node_modules
    echo "Installing npm dependancies inside node_modules ..."
    npm install
fi

echo "Installation done!"
