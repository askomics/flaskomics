#! /bin/bash

config_template_path="config/askomics.ini.template"
config_path="config/askomics.ini"

tmpfile=$(mktemp /tmp/askomics.ini.XXXXXX)

# Init config file
cp $config_template_path $tmpfile

# Convert env to ini entry
printenv | egrep "ASKO_" | while read setting
do
    section=$(echo $setting | egrep -o "^ASKO[^=]+" | sed 's/^.\{5\}//g' | cut -d "_" -f 1)
    key=$(echo $setting | egrep -o "^ASKO[^=]+" | sed 's/^.\{5\}//g' | sed "s/$section\_//g")
    value=$(echo $setting | egrep -o "=.*$" | sed 's/^=//g')
    # crudini --set ${tmpfile} "${section}" "${key}" "${value}"
    python3 cli/config_updater.py -p $tmpfile -s "${section}" -k "${key}" -v "${value}"
done

# config ready, copy to dest
cp $tmpfile $config_path
