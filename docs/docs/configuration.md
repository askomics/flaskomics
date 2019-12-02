AskOmics configuration is stored in `config/askomics.ini` file.

- flask

    - `debug` (`true` or `false`): Set to true if you run AskOmics in development mode, or for debug purpose
    - `secret_key` (string): AskOmics secret key for session.
    - `session_timeout` (int): timeout for the session cookie (in minutes)

- celery

    - `broker_url` (url): Redis or RabitMQ url
    - `result_backend` (url): Redis or RabitMQ url

- askomics

    - `debug` (`true` or `false`): Display debug log in console
    - `debug_ttl` (`true` or `false`): Keep converted rdf file. Set the to true can fill you disk, active only for debug purpose
    - `reverse_proxy_path` (string): proxy path if AskOmics is accessible under a subpath
    - `subtitle` (string): Subtitle, displayed on the browser tab
    - `footer_message` (string): Custom message displayed on the AskOmics footer
    - `display_commit_hash` (`true` or `false`): diplay the commit hash of the current version in the AskOmics footer
    - `data_directory` (path): where AskOmics store the data 
    - `database_path` (path): Path to the sqlite database
    - `npreview` (int): Number of line displayed during integration 
    - `password_salt` (string): Password salt 
    - `default_locked_account` (`true` or `false`): Lock new account
    - `disable_integration` (`true` or `false`): Disable integration to non admin users
    - `quota` (size): Default quota for new users

- virtuoso

    - `triplestore` (string): Triplestore used. Can be virtuoso, fuseki or corese 
    - `endpoint` (url): Triplestore endpoint url 
    - `updatepoint` (url): Triplestore updatepoint url 
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
    - `prefix` (url): Default AskOmics prefix 
    - `namespace` (url): Default AskOmics namespace 
    - `preview_limit` (int): Number of line to be previewed in the results page 
    - `result_set_max_rows` (int): Triplestore max row. Must be the same as SPARQL[ResultSetMaxRows] in virtuoso.ini config

- federation

    - `query_engine` (string): Query engine to use, can be corese or fedx
    - `endpoint` (url): Federated query engine endpoint url
    - `local_endpoint` (url): Triplestore url, accessible from the federated query engine 

- sentry

    - `server_dsn` (url): Sentry url for the server
    - `frontend_dsn` (url): Sentry url for the frontend
