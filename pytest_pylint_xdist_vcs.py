"""Pylint plugin for py.test"""
from os import sep
from os.path import dirname
from os.path import exists
from os.path import join
import re

from six.moves.configparser import (  # pylint: disable=import-error
    ConfigParser,
    NoSectionError,
    NoOptionError
)
from pylint import lint
from pylint.config import PYLINTRC
from pylint.interfaces import IReporter
from pylint.reporters import BaseReporter
import pytest

import svn


SCM_LIST = [svn]


class PyLintException(Exception):
    """Exception to raise if a file has a specified pylint error"""


class ProgrammaticReporter(BaseReporter):
    """Reporter that replaces output with storage in list of dictionaries"""

    __implements__ = IReporter
    name = 'pylint-vcs-reporter'
    extension = 'prog'

    def __init__(self, output=None):
        BaseReporter.__init__(self, output)
        self.data = []

    def handle_message(self, msg):
        """Get message and append to our data structure"""
        self.data.append(msg)

    def _display(self, layout):
        """launch layouts display"""


def get_rel_path(path, parent_path):
    """
    Give the path to object relative to ``parent_path``.
    """
    replaced_path = path.replace(parent_path, '', 1)
    if replaced_path[0] == sep:
        rel_path = replaced_path[1:]
    else:
        rel_path = replaced_path
    return rel_path


def pytest_addoption(parser):
    """Add plugin command line options to pytest command line options"""
    group = parser.getgroup("general")
    group.addoption(
        "--pylint",
        action='store_true', default=False,
        help="run pylint on all python files"
    )
    group.addoption(
        "--pylint-vcs",
        action='store_true', default=False,
        help="run pylint only on python files changed in current rev. \
        If not SCM working copy detected it fallbacks to --pylint option"
    )
    group.addoption(
        '--no-pylint',
        action="store_true", default=False,
        help='disable running pylint'
    )
    group.addoption(
        '--pylint-no-vcs',
        action="store_true", default=False,
        help='Disable vcs files linting mode. Note: this option does not turn off pylint'
    )
    group.addoption(
        '--pylint-rcfile',
        default=None,
        help='Location of RC file if not pylintrc'
    )


def pytest_sessionstart(session):
    """Storing pylint settings on the session"""
    config = session.config
    terminal_reporter = config.pluginmanager.get_plugin('terminalreporter')
    capture_manager = config.pluginmanager.get_plugin('capturemanager')
    session.pylint_enabled = config.option.pylint or config.option.pylint_vcs and not config.option.no_pylint

    if session.pylint_enabled:
        session.pylint_config = None
        session.pylintrc_file = None
        session.pylint_ignore = []
        session.pylint_ignore_patterns = []
        session.pylint_msg_template = None

        if config.option.pylint_vcs:
            if not config.option.pylint_no_vcs:
                scm, scm_root = _get_vcs_root(str(config.rootdir))
                if scm:
                    session.pylint_vcs_enabled = True
                    session.pylint_vcs_changed_filepaths = scm.get_mod_files(scm_root)
                    with capture_manager.global_and_fixture_disabled():
                        terminal_reporter.write('VCS working copy detected. VCS linting mode enabled\n')
                else:
                    with capture_manager.global_and_fixture_disabled():
                        terminal_reporter.write(
                            'No VCS working copy detected. VCS linting mode disabled: linting all the files\n')

        # Find pylintrc to check ignore list
        pylintrc_file = config.option.pylint_rcfile or PYLINTRC

        if pylintrc_file and not exists(pylintrc_file):
            # The directory of pytest.ini got a chance
            pylintrc_file = join(dirname(str(config.inifile)), pylintrc_file)

        if pylintrc_file and exists(pylintrc_file):
            session.pylintrc_file = pylintrc_file
            session.pylint_config = ConfigParser()
            session.pylint_config.read(pylintrc_file)

            try:
                ignore_string = session.pylint_config.get('MASTER', 'ignore')
                if ignore_string:
                    session.pylint_ignore = ignore_string.split(',')
            except (NoSectionError, NoOptionError):
                pass

            try:
                session.pylint_ignore_patterns = session.pylint_config.get(
                    'MASTER', 'ignore-patterns')
            except (NoSectionError, NoOptionError):
                pass

            try:
                session.pylint_msg_template = session.pylint_config.get(
                    'REPORTS', 'msg-template'
                )
            except (NoSectionError, NoOptionError):
                pass


def pytest_report_header(config, startdir):
    """Add the message_ix import path to the pytest report header."""
    if 'pylint_no_vcs' in config.option:
        return 'VCS linting mode set to disabled'
    return None


def include_file(path, ignore_list, ignore_patterns=None):
    """Checks if a file should be included in the collection."""
    if ignore_patterns:
        for pattern in ignore_patterns:
            if re.match(pattern, path):
                return False
    parts = path.split(sep)
    return not set(parts) & set(ignore_list)


def pytest_collect_file(path, parent):
    """Collect files on which pylint should run"""
    item = None

    if not parent.session.pylint_enabled:
        return None
    if path.ext != '.py':
        return None

    if getattr(parent.session, 'pylint_vcs_enabled', False):
        if str(path) in parent.session.pylint_vcs_changed_filepaths:
            item = PyLintItem(path, parent)
    else:
        rel_path = get_rel_path(str(path), str(parent.session.fspath))
        session = parent.session
        if session.pylint_config is None:
            item = PyLintItem(path, parent)
        elif include_file(rel_path, session.pylint_ignore, session.pylint_ignore_patterns):
            item = PyLintItem(path, parent, session.pylint_msg_template, session.pylintrc_file)
    return item


class PyLintItem(pytest.Item, pytest.File):
    """pylint test running class."""
    # pylint doesn't deal well with dynamic modules and there isn't an
    # astng plugin for pylint in pypi yet, so we'll have to disable
    # the checks.
    # pylint: disable=no-member,abstract-method
    def __init__(self, fspath, parent, msg_format=None, pylintrc_file=None):
        super(PyLintItem, self).__init__(fspath, parent)

        self.add_marker('pylint')
        self._nodeid = self.nodeid + '[pylint]'

        self.rel_path = get_rel_path(
            fspath.strpath,
            parent.session.fspath.strpath
        )

        if msg_format is None:
            self._msg_format = '{C}:{line:3d},{column:2d}: {msg} ({symbol})'
        else:
            self._msg_format = msg_format

        self.pylintrc_file = pylintrc_file

    def runtest(self):
        """Check the pylint messages to see if any errors were reported."""
        reported_errors = []
        reporter = ProgrammaticReporter()
        args_list = [self.fspath.strpath]

        if self.pylintrc_file:
            args_list.append('--rcfile={0}'.format(self.pylintrc_file))
        result = lint.Run(args_list, reporter=reporter, do_exit=False)

        errors = result.linter.reporter.data
        for error in errors:
            reported_errors.append(
                error.format(self._msg_format)
            )
        if reported_errors:
            raise PyLintException('\n'.join(reported_errors))

    def repr_failure(self, excinfo): # pylint: disable=arguments-differ
        """Handle any test failures by checkint that they were ours."""
        if excinfo.errisinstance(PyLintException):
            return excinfo.value.args[0]
        return super(PyLintItem, self).repr_failure(excinfo)

    def reportinfo(self):
        """Generate our test report"""
        return self.fspath, None, '[pylint] {0}'.format(self.rel_path)


def _get_vcs_root(path):
    """Returns the vcs module and the root of the repo.
    Returns:
      A tuple containing the vcs module to use (svn, git) and the root of the
      repository. If repository is unidentified,  then (None, None) is returned.
    """
    for vcs in SCM_LIST:
        repo_root = vcs.repository_root(path)
        if repo_root:
            return vcs, repo_root

    return (None, None)
