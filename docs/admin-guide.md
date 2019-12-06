## Deploy a production instance

In production, AskOmics is deployed with docker and docker-compose. We provide `docker-compose.yml` templates to deploy your instance.

### Prerequisites

Install `git`

```bash
# Debian/Ubuntu
apt install -y git
# Fedora
dnf install -y git
```

Install `docker`:

- [Debian](https://docs.docker.com/install/linux/docker-ce/debian/)
- [Ubuntu](https://docs.docker.com/install/linux/docker-ce/ubuntu/)
- [Fedora](https://docs.docker.com/install/linux/docker-ce/fedora/)

Install `docker-compose`:

```bash
# Debian/Ubuntu
apt install -y docker-compose
# Fedora
dnf install -y docker-compose
```

### Deployment

#### Download templates

First, clone the [flaskomics-docker-compose](https://github.com/askomics/flaskomics-docker-compose) repository. It contain template files to deploy your AskOmics instance.


```bash
git clone https://github.com/askomics/flaskomics-docker-compose.git
```

This repo contains several directories, depending on your needs

```bash
cd flaskomics-docker-compose
ls -1
```

Two directories are used for production deployment

- `standalone`: deploy AskOmics with all its dependencies for a standalone usage
- `federated`: deploy AskOmics with all its dependencies for a federated usage (Ask external endpoint such as [NeXtProt](https://sparql.nextprot.org))

Choose one of this directory depending of your needs

```bash
cd federated
```
#### Configure

First, edit the `docker-compose.yml` file. You can change the following entries:

- `services` > `askomics` > `image`: Use the [latest](https://github.com/askomics/flaskomics/releases/latest) image tag. Example: `askomics/flaskomics:3.2.1` 
- `services` > `virtuoso` > `image`: Use the [latest](https://github.com/askomics/flaskomics/releases/latest) image tag. Example: `askomics/virtuoso:7.2.5.1` 
- `services` > `nginx` > `ports`: You can change the default port if `80` is already used on your machine. Example: `"8080:80"`

##### Virtuoso

Then, configure virtuoso by editing `virtuoso.env`

Edit `VIRT_Parameters_NumberOfBuffers` and `VIRT_Parameters_MaxDirtyBuffers` following rules described [here](https://github.com/askomics/flaskomics-docker-compose#configure-virtuoso).

!!! warning
    Change the `DBA_PASSWORD` if you plan to expose the virtuoso endpoint.

##### Nginx (web proxy)

Nginx is used to manage web redirection. Nginx configuration is in two files: `nginx.conf` and `nginx.env`. If you want to access the virtuoso endpoint, uncomment the `virtuoso` section in `nginx.conf`


##### AskOmics

AskOmics configuration is set using enviroment variables. This variables are set in `askomics.env`. All entry if the `askomics.ini` file can be overrided in this file using 


All properties defined in `askomics.ini` can be configured via the environment variables in `askomics.env`. The environment variable should be prefixed with `ASKO_` and have a format like `ASKO_$SECTION_$KEY`. $SECTION and $KEY are case sensitive. *E.g.* property `footer_message` in the `askomics` section should be configured as `ASKO_askomics_footer_message=Welcome to my AskOmics!`

!!! warning
    Change `ASKO_flask_secret_key` and `ASKO_askomics_password_salt` to random string

## Configuration

AskOmics configuration is stored in `config/askomics.ini` file.

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

- `virtuoso`

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

- `federation`

    - `query_engine` (string): Query engine to use, can be corese or fedx
    - `endpoint` (url): Federated query engine endpoint url
    - `local_endpoint` (url): Triplestore url, accessible from the federated query engine 

- `sentry`

    - `server_dsn` (url): Sentry url for the server
    - `frontend_dsn` (url): Sentry url for the frontend
