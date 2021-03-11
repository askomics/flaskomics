# Command line interface

Several commands are available to help manage your instance. These commands are available through `make` when launched from the same directory as the *Makefile*. (If you are running Askomics in a docker container, you will need to connect to it to launch these commands)

You can run the `make help` command to get a list of available admin commands.

# Updating namespaces

Version 4.2 added the `/data/<uri>` route showing the properties linked to a node.
To make sure that your URIs are properly redirecting to this route, you should make sure that the `namespace_data` and `namespace_internal` [configuration option](configure.md) are set to your instance *url*. Make sure to match either `http` or `https` depending on your instance, and don't forget `/data/` or `/internal/`.

## Updating an existing instance
If you changed the namespaces after having already integrated some files, you will need to run two additional commands to update your existing data.

- `make update-base-url`
You will be prompted to enter the previous namespace url, and then the new one.
You can either enter a partial namespace url (ex: `http://askomics.org/`) or the full one (ex: `http://askomics.org/data/`)
In the latter case, you will need to run the command twice (once for each namespace)

- `make clear-cache`
This will clear the abstraction cache, making sure your data is synchronized with the new namespaces.
