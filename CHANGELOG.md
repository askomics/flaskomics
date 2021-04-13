# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

This changelog was started for release 4.2.0.

## [4.2.0] - 2021-03-15

### Added

- Added File view in admin interface. Administrators can delete the files.
- Added Dataset view in admin interface. Administrators can delete the datasets, and make them public/private.
- Added Public queries view in admin interface. Administrators can make them private.
- Added /data/<uri> route, which list parameters (predicates and objects) for a specific URI. Results are filtered based on the user's visibility.
- Added CLI script for changing Askomics namespace if some files have already been integrated.
- Added documentation related to the previous CLI script.
- Added `enable_sparql_console` related to the console change (in *changed*)

### Changed

- Restricted SPARQL query api endpoint to administrators. It can be re-enabled for logged user with the `enable_sparql_console` configuration value. WARNING: Check (#169) .
- Set the SPARQL console read-only for non-administrators. It can be re-enabled for logged user with the `enable_sparql_console` configuration value. WARNING: Check (#169)

### Fixed

- Fixed encoding issue (#160)
- Fixed filename issue (#155)
- Fixed retrocompatibility issue (#148)

### Security

- Bumped ini from 1.3.5 to 1.3.7
- Bumped axios from 0.20.0 to 0.21.1
- Bumped prismjs from 1.21.0 to 1.23.0
- Bumped elliptic from 6.5.3 to 6.5.4
- Bumped react-addons-update from 15.6.2 to 15.6.3
- Bumped react-force-graph from 1.36.10 to 1.39.2
- Bumped react-syntax-highlighter from 13.5.3 to 15.4.3