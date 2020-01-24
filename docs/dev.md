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



## Contribute to AskOmics


### Issues

If you have an idea for a feature to add or an approach for a bugfix, it is best to communicate with developers early. The most common venues for this are [GitHub issues](https://github.com/askomics/flaskomics/issues/).

### Pull requests

All changes to AskOmics should be made through pull requests to [this](https://github.com/askomics/flaskomics) repository.

[Install AskOmics in development mode](dev.md#install-askomics), then, create a new branch for your new feature

```bash
git checkout -b my_new_feature
```

Commit and push your modification to your [fork](https://help.github.com/articles/pushing-to-a-remote/). If your changes modify code, please ensure that is conform to [AskOmics style](#coding-style-guidlines)

Write tests for your changes, and make sure that they [passes](dev.md#launch-continuous-integration-locally).

Open a pull request against the master branch of flaskomics. The message of your pull request should describe your modifications (why and how).

The pull request should pass all the continuous integration tests which are automatically run by Github using Travis CI. The coverage must be at least remain the same (but it's better if it increases)


### Coding style guidelines

#### General

Ensure all user-enterable strings are unicode capable. Use only English language for everything (code, documentation, logs, comments, ...)

#### Python

We follow [PEP-8](https://www.python.org/dev/peps/pep-0008/), with particular emphasis on the parts about knowing when to be inconsistent, and readability being the ultimate goal.

- Whitespace around operators and inside parentheses
- 4 spaces per indent, spaces, not tabs
- Include docstrings on your modules, class and methods
- Avoid from module import \*. It can cause name collisions that are tedious to track down.
- Class should be in `CamelCase`, methods and variables in `lowercase_with_underscore`

#### Javascript

We follow [W3 JavaScript Style Guide and Coding Conventions](https://www.w3schools.com/js/js_conventions.asp)

### Contribute to docs

all the documentation (including what you are reading) can be found [here](https://flaskomics.readthedocs.io). Files are on the [AskOmics repository](https://github.com/askomics/flaskomics/tree/master/docs).

To serve docs locally, run

```bash
cd flaskomics
# source the askomics virtual env
source venv/bin/activate
mkdocs serve
```

Docs are available at [localhost:8000](localhost:8000)
