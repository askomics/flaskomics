
## Deploy a development instance

In development mode, AskOmics dependencies can be deployed with docker-compose, but AsKomics have to be running locally, on your dev machine.

### Prerequisites

Install dev dependencies


```bash
# Debian/Ubuntu
sudo apt install -y git python3 python3-venv python3-dev make gcc zlib1g-dev libbz2-dev liblzma-dev g++ npm
# Fedora
sudo dnf install -y git make gcc zlib-devel bzip2-devel xz-devel python3-devel gcc-c++ npm
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

### Deploy dependencies

We provide a `docker-compose` template to run external services used by AskOmics. Clone the [flaskomics-docker-compose](https://github.com/askomics/flaskomics-docker-compose) repository to use it.

```bash
git clone https://github.com/askomics/flaskomics-docker-compose.git
```

Use the `dev` directory

```bash
cd flaskomics-docker-compose/dev
```

Deploy dockers

```bash
docker-compose up -d
```

### Fork and clone AskOmics repository


[Fork](https://help.github.com/articles/fork-a-repo/) the AskOmics repository

then, clone your fork locally

```bash
git clone https://github.com/USERNAME/flaskomics.git # replace USERNAME with your github username
```

### Install AskOmics

Use the `install.sh` script to setup the python virtual environment and to download python and node modules needed.

```bash
./install.sh
```

### Run

Run in dev mode

```bash
./run_all.sh -d dev
```

## Launch continuous integration locally

AskOmics have to pass the continuous integration. To run the CI locally, you can use `test.sh`. The CI use `config/askomics.test.ini` for the configuration. You can use the `ci/docker-compose.yml` of [flaskomics-docker-compose](https://github.com/askomics/flaskomics-docker-compose) to deploy clean third party apps used by AskOmics on the right port.








