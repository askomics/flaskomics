# Make commands

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

# Single tenant mode

Starting from release 4.4, the *Single tenant mode* is available through a configuration option.
In Virtuoso, aggregating multiples graphs (using several FROM clauses) can be very costly for big/numerous graphs.

Single tenant mode send all queries on all stored graphs, thus speeding up the queries. This means that **all graphs are public, and can be queried by any user**. This affect starting points, abstractions, and query.

!!! warning
    If you are storing sensitive data on AskOmics, make sure to disable anonymous access and account creation when using *Single tenant mode*.

!!! warning
    *Single tenant mode* has no effect on federated queries

# Administrator panel

Administrators have access to a specific panel in AskOmics.
This <navbar><i class="fa fa-chess-king"></i> Admin</navbar> tab can be found after clicking on <navbar><i class="fa fa-user"></i> *Your Name &#9662;*</navbar>.

## User management

From the <navbar><i class="fa fa-chess-king"></i> Admin</navbar> tab, administrators are able to:

- Create a new user account
- Manage existing user accounts
    - Blocking an user account
    - Setting an user as an administrator
    - Updating an user's individual storage quota
    - Deleting an user

They will also be able to check the last time of activity of an user.

## Files

A list of all uploaded files is available. Administrators can delete a file at any time.

## Datasets

All currently stored datasets are available. Administrators can publish, unpublish, and delete them.

## Forms / Templates

A list of **public** forms and templates is available. Administator can unpublish them if need be.

# Anonymous query

Starting from release 4.5, the *Anonymous query mode* is available through a configuration option.
This option allows anonymous users to create full queries (not only previews), and access the results/sparql console associated.

To avoid overloading the server, anonymous queries are regularly deleted. (Every hour for failed queries, and every X days for successful jobs, as defined by the *anonymous_query_cleanup* variable (default 60)).

!!! warning
    Anonymous users cannot create forms/templates, but admin can from the admin panel.
    Do keep in mind that anonymous jobs will be deleted at some point.

!!! warning
    If you disable the *anonymous_query*, the job cleaner will not run. You will need to delete the jobs manually from the admin panel.
