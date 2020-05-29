In production, AskOmics is deployed with docker and docker-compose. We provide `docker-compose.yml` templates to deploy your instance.

# Prerequisites

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

# Deploy

## Download templates

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
## Configure

First, edit the `docker-compose.yml` file. You can change the main port:

- `services` > `nginx` > `ports`: You can change the default port if `80` is already used on your machine. Example: `"8080:80"` to use `8080` instead of `80`.

### Virtuoso

Then, configure virtuoso by editing `virtuoso.env`

Edit `VIRT_Parameters_NumberOfBuffers` and `VIRT_Parameters_MaxDirtyBuffers` following rules described [here](https://github.com/askomics/flaskomics-docker-compose#configure-virtuoso).

!!! warning
    Change the `DBA_PASSWORD` if you plan to expose the virtuoso endpoint. The password endpoint have to be the same in `askomics.env` > `ASKO_triplestore_password`

### Nginx (web proxy)

Nginx is used to manage web redirection. Nginx configuration is in two files: `nginx.conf` and `nginx.env`. If you want to access the virtuoso endpoint, uncomment the `virtuoso` section in `nginx.conf`


### AskOmics

All properties defined in `askomics.ini` can be configured via the environment variables in `askomics.env`. The environment variable should be prefixed with `ASKO_` and have a format like `ASKO_$SECTION_$KEY`. $SECTION and $KEY are case sensitive. *E.g.* property `footer_message` in the `askomics` section should be configured as `ASKO_askomics_footer_message=Welcome to my AskOmics!`.

!!! warning
    Change `ASKO_flask_secret_key` and `ASKO_askomics_password_salt` to random string

For more information about AskOmics configuration, see [configuration](configure.md) section.

#### First user

environment variables can also be used to create a user into AskOmics at first start. For this, use `CREATE_USER=true` User information can be configured with the following environment variables:

- `USER_FIRST_NAME`: User first name (default: Ad)
- `USER_LAST_NAME`: User last name (default: Min)
- `USER_USERNAME`: Username (default: admin)
- `USER_PASSWORD`: Password (default: admin)
- `USER_EMAIL`: User email (default: admin@example.com)
- `USER_APIKEY`: User API key (default: admin)
- `GALAXY_API_KEY`: Galaxy URL linked to the user (optional)
- `GALAXY_URL`: User Galaxy API Key (optional)

The user will be created only if the users table of the database is empty.