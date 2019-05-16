# FlaskOmics

[![Build Status](https://travis-ci.org/xgaia/flaskomics.svg?branch=master)](https://travis-ci.org/xgaia/flaskomics)
[![Coverage Status](https://coveralls.io/repos/github/xgaia/flaskomics/badge.svg?branch=master)](https://coveralls.io/github/xgaia/flaskomics?branch=master)


FlaskOmics is the future of [AskOmics](https://github.com/askomics/askomics).

## Dependencies

FlAskOmics need a triplestore and a redos database to run.

### Redis

```bash
sudo apt install redis
```

### Virtuoso

[virtuoso](https://github.com/openlink/virtuoso-opensource)


## Requirements

Python3, Python3 virtual env and npm

```bash
sudo apt install python3 python3-venv npm
```

## Install
```bash
./install.sh
```

## Run

```bash
run_all.sh -d dev
```

FlaskOmics is available at http://localhost:5000