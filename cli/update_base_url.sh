#! /bin/bash

echo "This script will update the base url in all graphs."
echo "You can specify either a base url (http://askomics.org/), or a full endpoint (http://askomics.org/data/)"
echo "Make sure to write a valid url (starting with either http:// or https://, and ending with a trailing /)"
echo ""
read -p "Old base url (ex: http://askomics.org/data/) : " OLD_URL
read -p "New base url (ex: http://my_new_url.com/data/) : " NEW_URL

python3 cli/update_base_url.py -c config/askomics.ini --old_url $OLD_URL --new_url $NEW_URL
