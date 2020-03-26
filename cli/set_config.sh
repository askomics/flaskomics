#! /bin/bash

config_template_path="config/askomics.ini.template"
config_path="config/askomics.ini"

# Create config file
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
    python3 cli/config_updater.py -p $config_path -s "${section}" -k "${key}" -v "${value}"
    $cmd
done
