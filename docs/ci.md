AskOmics continuous integration is composed of code linting and unit tests on the Python API. CI is launched automaticaly on the [askomics](https://github.com/askomics/flaskomics) repository on every pull requests. No PR will be merged if the CI fail.


# Setup CI environment

AskOmics CI need a clean environment. To get it, use `ci/docker-compose.yml` of [flaskomics-docker-compose](https://github.com/askomics/flaskomics-docker-compose). This file will deploy all dependencies on ports specified in `config/askomics.test.ini`.

```bash
git clone https://github.com/askomics/flaskomics-docker-compose
cd flaskomics-docker-compose/ci
docker-compose up -d
```

# Run CI locally

First, [install askomics in dev mode](/dev-deployment/#install-askomics).

Use `make test` to launch the CI.
