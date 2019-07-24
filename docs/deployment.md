# Deployment


## User

### Manual installation

#### Dependencies

##### Virtuoso

AskOmics work with an RDF triplestore.

[Compile virtuoso](https://github.com/openlink/virtuoso-opensource/blob/develop/7/README) or install it with [docker](https://github.com/askomics/docker-virtuoso)

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

Clone the [askomics-docker-compose](https://github.com/xgaia/flaskomics-docker-compose) repository


```bash
# clone
git clone https://github.com/xgaia/flaskomics-docker-compose.git
# cd
cd flaskomics-docker-compose
```

Update config (see [README](https://github.com/xgaia/flaskomics-docker-compose/blob/master/README.md))

Run

```bash
sudo docker-compose up -d
```

AskOmics will be available at [localhost](localhost).

## Developer


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

