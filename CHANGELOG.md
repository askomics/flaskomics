# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

This changelog was started for release 4.2.0.

## Unreleased

### Fixed

- Fixed an issue with forms (missing field and entity name for label & uri fields) (Issue #255)
- Fixed an issue with the data endpoint for FALDO entities (Issue #279)

### Added

- Added 'scaff' for autodetection of 'reference' columns
- Added a 'Label' column type: only for second column in CSV files. Will use this value if present, else default to old behavior
- Added button to hide FALDO relations (*included_in*)
- Added 'target=_blank' in query results
- Remote upload is now sent in a Celery task
- Added 'Status' for files (for celery upload, and later for better file management)
- Added tooltips to buttons in the query form (and other forms)
- Added owl integration

### Changed

- Changed "Query builder" to "Form editor" in form editing interface
- Changed abstraction building method for relations. (Please refer to #248 and #268)
- Changed abstraction building method for 'strand': only add the required strand type, and not all three types (#277)
- Updated documentation
- Changed the sparql endpoint: now use the authenticated SPARQL endpoint instead of public endpoint. Write permissions are not required anymore

### Removed

- Removed "Remote endpoint" field for non-ttl file
- Removed "Custom_uri" field for ttl file

### Security

- Bump axios from 0.21.1 to 0.21.2
- Bump tar from 6.1.0 to 6.1.11
- Bump @npmcli/git from 2.0.6 to 2.1.0
- Bump path-parse from 1.0.6 to 1.0.7
- Bump prismjs from 1.23.0 to 1.27.0
- Bump simple-get from 2.8.1 to 2.8.2
- Bump ssri from 6.0.1 to 6.0.2 
- Bump follow-redirects from 1.14.4 to 1.14.8
- Bump mkdocs from 1.0.4 to 1.2.3 in /docs
- Bump python-ldap from 3.3.1 to 3.4.0

## [4.3.1] - 2021-06-16

### Fixed

- Fixed an issue with categories
- Fixed an issue with GFF import

## [4.3.0] - 2021-06-10

### Added

- Added 'Date' entity type, with associated Date picker in UI
- Added API-key authentication for most endpoints. The api key should be passed with the header "X-API-KEY".
- Added CLI (using token-auth) (https://github.com/askomics/askoclics). Still a WIP, with the python package 'askoclics'.
- "Not" filter for categories
- URI management in first column (and link column). Manage both full URI and CURIE. Check #223 for details.
- 'Forms' : Minimal templates (users only access a basic form for modifying parameters, and not the graph) Restricted to admins. Form creators can customized entities and attributes display names to improve usability.

### Changed

- Faldo entity "Strand" now default to "faldo:BothStrandPosition" when the value is empty. The label will be "unknown/both" for CSV. For GFF and BED, "." will be "faldo:BothStrandPosition" instead of being ignored.
- If one of the column name of a CSV file is empty, raise an Exception.
- Now return the created result id (instead of celery task id) in the sparql query endpoint
- Now return the created file id (instead of celery task id) in the create file endpoint
- Fixed Flask version to < 2.0.0 due to compatibility issues

### Fixed

- Fixed the console restriction to admin/users (was not fully functional)
- Fixed an issue with spaces (and other characters) in URIs
- Fixed an issue with "Optional" button when using categories (and faldo entities) (either wrong values or nothing showing up) (Cf Changed category)
- Fixed table ordering in results for numerical values (they were managed as strings)
- Fixed UNION and MINUS blocks
- Fixed an issue with Faldo "same strand" (clicking on the link between Faldo nodes)
- Fixed Node/Link filter issue when using values with caps.

### Security

- Bump hosted-git-info from 2.8.8 to 2.8.9

## [4.2.2] - 2021-06-09

### Fixed

- Fixed startup issue: race condition on config file creation

## [4.2.1] - 2021-03-29

### Fixed

- Fixed issues with lock files

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
