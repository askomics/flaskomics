# Use with external endpoint


AskOmics can be use to explore external endpoint such as [NeXtProt](https://sparql.nextprot.org).

## Build external endpoint abstraction

First, build AskOmics abstraction of the external enpoint with [Abstractor](https://github.com/xgaia/abstractor).

Install Abstractor in a python virtual env

```bash
# Create and source venv
python3 -m venv venv
source venv/bin/activate
# Install Abstractor
pip install abstractor
```

Generate AskOmics abstraction. The tool explore the entire endpoint, so it can be long.

```bash
# Need help ?
abstractor -h
# Generate abstraction
abstractor -e <enpoint_url> -p <main_prefix> -o abstraction.ttl
```

## Deploy AskOmics

Deploy AskOmics with a special configuration to use it with an external endpoint. The following ini entry have to be updated:

- `askomics`
    - `disable_integration`: `true`

- `triplestore`
    - `external_endpoint`: <endpoint_url>
    - `prefix` = <main_prefix>
    - `namespace` = <main_prefix>


## Integrate external endpoint

Create an account on the AskOmics instance. The first account is an admin account who can integrate datasets. Load the `asbtraction.ttl` and integrate it has a public dataset.

Other users can't integrate datasets, but they can explore the external endpoint.
