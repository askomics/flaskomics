All AskOmics configuration is set in `config/askomics.ini` files. When AskOmics is deployed with `docker-compose`, configuration is set with environment variables. The environment variable should be prefixed with `ASKO_` and have a format like `ASKO_$SECTION_$KEY`. $SECTION and $KEY are case sensitive. *E.g.* property `footer_message` in the `askomics` section should be configured as `ASKO_askomics_footer_message=Welcome to my AskOmics!`

- `flask`

    - `debug` (`true` or `false`): Set to true if you run AskOmics in development mode, or for debug purpose
    - `secret_key` (string): AskOmics secret key for session.
    - `session_timeout` (int): timeout for the session cookie (in minutes)

- `celery`

    - `broker_url` (url): Redis or RabitMQ url
    - `result_backend` (url): Redis or RabitMQ url

- `askomics`

    - `debug` (`true` or `false`): Display debug log in console
    - `debug_ttl` (`true` or `false`): Keep converted rdf file. Set the to true can fill you disk, active only for debug purpose
    - `reverse_proxy_path` (string): Proxy path if AskOmics is accessible under a subpath
    - `subtitle` (string): Subtitle, displayed on the browser tab
    - `footer_message` (string): Custom message displayed on the AskOmics footer
    - `display_commit_hash` (`true` or `false`): diplay the commit hash of the current version in the AskOmics footer
    - `data_directory` (path): Where AskOmics store the data
    - `database_path` (path): Path to the sqlite database
    - `disable_account_creation` (`true` or `false`): disable the possibility to create new accounts
    - `npreview` (int): Number of line displayed during integration
    - `password_salt` (string): Password salt
    - `disable_account_creation` (`true` or `false`): Disable new account creation
    - `default_locked_account` (`true` or `false`): Lock new account
    - `disable_integration` (`true` or `false`): Disable integration to non admin users
    - `protect_public` (`true` or `false`): Public datasets and queries are visible only for logged users
    - `enable_sparql_console`(`true` or `false`): Allow non-admin logged users to use the sparql console. **This is unsafe.**
    - `quota` (size): Default quota for new users (can be customized individually later)
    - `github` (url): Github repository URL
    - `instance_url` (url): Instance URL. Used to send link by email when user reset his password
    - `smtp_host` (url): SMTP host url
    - `smtp_port` (int): SMTP port
    - `smtp_user` (string): SMTP user
    - `smtp_sender` (email): SMTP sender
    - `smtp_password` (string): SMTP password
    - `smtp_connection` (string): SMTP connectin (starttls or null)
    - `ldap_auth` (`true` or `false`): Use LDAP authentication
    - `ldap_host` (string):LDAP host
    - `ldap_port` (int): LDAP port
    - `ldap_bind_dn` (string): LDAP bind DN string
    - `ldap_bind_password` (strig): LDAP password
    - `ldap_search_base` (string): LDAP search base
    - `ldap_user_filter` (string): LDAP user filter
    - `ldap_username_attribute` (string): Username attribute
    - `ldap_first_name_attribute` (string): First name attribute
    - `ldap_surname_attribute` (string): Surname attribute
    - `ldap_mail_attribute` (string): Mail attribute
    - `ldap_password_reset_link` (url): Link to manage the LDAP password
    - `ldap_account_link` (url): Link to the LDAP account manager
    - `autocomplete_max_results` (int): Max results queries by autocompletion
    - `single_tenant` (bool): Enable [single tenant mode](/manage/#single-tenant-mode)

- `virtuoso`

    - `triplestore` (string): Triplestore used. Can be virtuoso, fuseki or corese
    - `endpoint` (url): Triplestore endpoint url
    - `updatepoint` (url): Triplestore updatepoint url
    - `isqlapi` (url): isql-api url when AskOmics use [isql-api](http://github.com/xgaia/isql-api) to perform queries on virtuoso through isql. If not set, AskOmics will launch queries on the SPARQL endpoint
    - `fuseki_upload_url` (url): If triplestore is fuseki, set the fuseki upload url
    - `username` (string): Triplestore credential: username
    - `password` (string): Triplestore credential: password
    - `load_url` (url): AskOmics url accessible from the triplestore
    - `upload_method` (string): upload method fir virtuoso. Can be load or insert
    - `chunk_size` (int): Number of RDF triples to upload in one time
    - `block_size` (int): Size of location bocksize for positionable entities
    - `serialization_format` (string): RDF serialization format. Can be `nt`, `turtle` or `xml`
    - `default_graph` (string): Triplestore default graph
    - `users_graph` (string): User base graph
    - `namespace_data` (url): AskOmics namespace for data. Correspond to the `:` prefix. You should change this to your instance url if you want your URIs to be resolved.
    - `namespace_internal` (url): AskOmics namespace for internal triples. Correspond to the `askomics:` prefix. You should change this to your instance url if you want your URIs to be resolved.
    - `preview_limit` (int): Number of line to be previewed in the results page
    - `result_set_max_rows` (int): Triplestore max row. Must be the same as SPARQL[ResultSetMaxRows] in virtuoso.ini config

- `federation`

    - `query_engine` (string): Query engine to use, can be corese or fedx
    - `endpoint` (url): Federated query engine endpoint url
    - `local_endpoint` (url): Triplestore url, accessible from the federated query engine

- `sentry`

    - `server_dsn` (url): Sentry url for the server
    - `frontend_dsn` (url): Sentry url for the frontend
