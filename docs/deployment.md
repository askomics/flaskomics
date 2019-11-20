# Deployment


## User

### Manual installation

#### Dependencies

##### Virtuoso

AskOmics work with an RDF triplestore.

[Compile virtuoso](https://github.com/openlink/virtuoso-opensource/blob/develop/7/README.md) or install it with [docker](https://github.com/askomics/docker-virtuoso)

##### Python3/venv/npm

AskOmics is build in python3 and javascript. Install the following packages

```bash
# ubuntu
apt install -y python3 python3-venv npm
# Fedora
dnf install -y python3 python3-venv npm
```

#### Installation with scripts

Install AskOmics with `install.sh` and run it with `run_all.sh`. AskOmics will be available at [localhost:5000](localhost:5000).


### Installation with docker-compose

Clone the [askomics-docker-compose](https://github.com/askomics/flaskomics-docker-compose) repository


```bash
# clone
git clone https://github.com/askomics/flaskomics-docker-compose.git
# cd
cd flaskomics-docker-compose/standalone
# Or, if you want to use federated queries
cd flaskomics-docker-compose/federated
```

Update config (see [README](https://github.com/askomics/flaskomics-docker-compose/blob/master/README.md))

Run

```bash
sudo docker-compose up -d
```

AskOmics will be available at [localhost](localhost).

### Installation with a single docker

Docker image [askomics/flaskomics-with-dependencies](https://cloud.docker.com/repository/docker/askomics/flaskomics-with-dependencies) contain AskOmics with all his dependencies (Redis, virtuoso, celery ...).

```bash
# Pull image
docker pull askomics/flaskomics-with-dependencies
# run image
docker run -d askomics/flaskomics-with-dependencies
```

If you need a persistent volume, run

```bash
docker run -d -v ./flaskomics-data:/tmp/flaskomics askomics/flaskomics-with-dependencies
```

The image create a default user at the first run. You can update this user by setting the following environment variables:

|ENV|User field|default value|
|----|----|----|
|`USER_FIRST_NAME`|First name|Ad|
|`USER_LAST_NAME`|Last name|Min|
|`USERNAME`|Username|admin|
|`USER_EMAIL`|Email|admin@example.org|
|`USER_PASSWORD`|Password (clear)|admin|
|`USER_APIKEY`|User api key|admin|
|`GALAXY_URL`|Galaxy url (optional)| |
|`GALAXY_API_KEY`|Galaxy api key (optional)| |

For example:

```bash
docker run -d -v ./flaskomics-data:/tmp/flaskomics -e USER_FIRST_NAME="John" -e USER_LAST_NAME="Wick" -e USERNAME="jwick" askomics/flaskomics-with-dependencies
```

## Developer

### AskOmics


[Fork](https://help.github.com/articles/fork-a-repo/) the AskOmics repository

then, clone your fork

```bash
git clone https://github.com/USERNAME/flaskomics.git # replace USERNAME with your github username
```

[Install AskOmics](#installation-with-scripts)

Run it with dev mod

```bash
./run_all.sh -d dev
```

AskOmics will be available at [localhost:5000](localhost:5000)

### Dependencies

Clone the [askomics-docker-compose](https://github.com/askomics/flaskomics-docker-compose) repository and go into the `dev` directory.

```bash
# clone
git clone https://github.com/askomics/flaskomics-docker-compose.git
# cd
cd flaskomics-docker-compose/dev
```

The `dev` directory contain a `docker-compose.yml` file who can lauch all dependencies needed by AskOmics (Virtuoso, Redis, Corese, Galaxy).

```bash
# clone
docker-compose up -d
```

Use the `ci` directory to lauch dockers for testing AskOmics

```bash
cd ../ci
docker-compose up -d
```
