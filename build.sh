#! /bin/bash

#####################################################
#                                                   #
#                  Build Javascript                 #
#                                                   #
#####################################################

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
        npm_depmode="prod"
    ;;
    dev|development)
        npm_depmode="dev"
    ;;
    *)
        echo "-d $depmode: wrong deployment mode"
        usage
        exit 1
esac

echo "Building Javascipt ..."
npm run $npm_depmode
