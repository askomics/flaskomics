# Contribute to AskOmics

## Issues

If you have an idea for a feature to add or an approach for a bugfix, it is best to communicate with developers early. The most common venues for this are [GitHub issues](https://github.com/xgaia/flaskomics/issues/).

## Pull requests

All changes to AskOmics should be made through pull requests to this repository.

For the [askomics repository](https://github.com/xgaia/flaskomics) to your account. To keep your copy up to date, you need to frequently [sync your fork](https://help.github.com/articles/syncing-a-fork/):

```bash
git remote add upstream https://github.com/xgaia/flaskomics
git fetch upstream
git checkout master
git merge upstream/master
```

Then, create a new branch for your new feature

```bash
git checkout -b my_new_feature
```

Commit and push your modification to your [fork](https://help.github.com/articles/pushing-to-a-remote/). If your changes modify code, please ensure that is conform to [AskOmics style](#coding-style-guidlines)

Write tests for your changes, and make sure that they [passes](#tests).

Open a pull request against the master branch of askomics. The message of your pull request should describe your modifications (why and how).

The pull request should pass all the continuous integration tests which are automatically run by Github using Travis CI. The coverage must be at least remain the same (but it's better if it increases)

## Tests

Use `test.sh` script to lint and test the code. Don't PR if linting or testing don't pass.


## Coding style guidelines

### General

Ensure all user-enterable strings are unicode capable. Use only English language for everything (code, documentation, logs, comments, ...)

### Python

We follow [PEP-8](https://www.python.org/dev/peps/pep-0008/), with particular emphasis on the parts about knowing when to be inconsistent, and readability being the ultimate goal.

- Whitespace around operators and inside parentheses
- 4 spaces per indent, spaces, not tabs
- Include docstrings on your modules, class and methods
- Avoid from module import \*. It can cause name collisions that are tedious to track down.
- Class should be in `CamelCase`, methods and variables in `lowercase_with_underscore`

### Javascript

We follow [W3 JavaScript Style Guide and Coding Conventions](https://www.w3schools.com/js/js_conventions.asp)

## Contribute to docs

all the documentation (including what you are reading) can be found [here](https://flaskomics.readthedocs.io). Files are on the [AskOmics repository](https://github.com/xgaia/flaskomics/tree/master/docs).

To preview the docs, run

```bash
cd flaskomics
# source the askomics virtual env
source venv/bin/activate
cd docs
make html
```

html files are in `build` directory.

