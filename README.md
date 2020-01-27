
[![Build Status](https://travis-ci.org/aleXOR2/pytest-pylint-xdist-vcs.svg?branch=master)](https://travis-ci.org/aleXOR2/pytest-pylint-xdist-vcs)
[![Coverage Status](https://coveralls.io/repos/github/aleXOR2/pytest-pylint-xdist-vcs/badge.svg?branch=master)](https://coveralls.io/github/aleXOR2/pytest-pylint-xdist-vcs?branch=master)
[![pypi](https://img.shields.io/pypi/l/pytest-pylint-xdist-vcs.svg)](https://pypi.python.org/pypi/pytest-pylint-xdist-vcs)
[![supported versions](https://img.shields.io/pypi/pyversions/pytest-pylint-xdist-vcs.svg)](https://pypi.python.org/pypi/pytest-pylint-xdist-vcs)

Table of Contents
=================

  * [Description](#description)
      * [Added](#added)
      * [Removed](#removed)
  * [Terminal output example](#terminal-output-example)
  * [Prerequisites](#prerequisites)
  * [Usage examples](#usage-examples)
  * [Embedding into conf files](#embedding-into-conf-files)
  * [Acknowledgements](#acknowledgements)

Description
================

Pytest Plugin for distributed linting with pylint of VCS controlled files.
This project is hypothetically can work with any pytest test parallelization plugin (pytest-parallel?) as it doesn't depend on any xdist specific design.

Differences between [pytest-pylint](https://github.com/carsongee/pytest-pylint.git) and this plug-in:

### Added

- pylint works in single job mode so that to allow parallelization with xdist
- when test result is printed into terminal (with `-v` verbose flag) it contains pylint tag `[pylint]`
- vcs mode enables linting only python files modified / added in the working copy latest revision

   If working copy not found, the linting falls back to "all files linting".

### Removed

- skipping of linted file that was already linted as it duplicates functionality of xdist (`mtimes`  cache recording)
- Python 2 and Pylint 1.x support
- `--pylint-jobs` option as multi processing managed by xdist
- display only particular error codes (option `--pylint-error-types` ) as it is already available via `.pylintrc` **Message Control** section

   See http://pylint.pycqa.org/en/latest/user_guide/message-control.html for detail

Terminal output example
=======================

Verbose output
   ```sh
   $ pytest -v --pylint -m pylint
   [gw0] [ 50%] PASSED tests/test_devices.py[pylint] <- tests/test_devices.py
   [gw0] [ 1000%] FAILED tests/test_environment.py[pylint] <- tests/test_environment.py
   ```

Non-verbose output (only filenames / modules displayed):

```sh
collected 2 items

mymodule/__init__.py[pylint] .                              [ 50%]
mymodule/test_file.py[pylint] F                             [100%]
```

Prerequisites
=============

* Linux OS
* SVN 1.8+ (for svn repo linting)
* Terminal locale set as UTF-8

   Plugin uses terminal locale and assumes that it is set as UTF-8 encoding (en_GB.utf8, pl_pl.utf8, ru_RU.utf8, etc)
* Python 3.5+

Usage examples
============

- this runs pylint for all error messages.

```bash
   py.test --pylint
```

- the same as above but utilizing all available processor cores.

```bash
   py.test --pylint --numprocesses=auto
```

- This would use the pylintrc file at /my/pyrc:

```shell
   py.test --pylint --pylint-rcfile=/my/pyrc
```

- You can restrict your test run to only perform pylint checks by typing:

```shell
    py.test --pylint -m pylint
```

If plugin runs the check of VCS working copy, then you can lint only files changed / added in the last revision

```shell
    py.test --pylint-vcs -m pylint
```

Embedding into conf files
============

You can embed this into setup.cfg:

```ini
[tool:pytest]
addopts= --pylint-vcs
```

or into tox.ini

```ini
[pytest]
addopts = --pylint-vcs
```

Acknowledgements
================

This code is a fork of 
[pytest-pylint](https://github.com/carsongee/pytest-pylint.git) 0.14.0
