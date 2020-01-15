# -*- coding: utf-8 -*-
"""Testing module for plugin"""
import os
from unittest.mock import patch
import subprocess

import pytest
from pytest import ExitCode
import py


pytest_plugins = ('pytester',)  # pylint: disable=invalid-name

MOCKED_REPO_LOCAL_PATH = str(py.path.local(os.getcwd()).join('test', 'mocked_repo')) # pylint: disable=no-member

SVN_STATUS_OUTPUT = '''
M       {}/some_data.txt
M       {}/python_package
 M       {}/python_package/__init__.py
M      {}/python_package/some_folder
A       {}/python_package/some_folder/test_file_two.py
?       {}/python_package/some_folder/some_other_data
D       {}/python_package/test_file_one.py
'''.format(*(MOCKED_REPO_LOCAL_PATH for _ in range(8)))
SVN_INFO_OUTPUT = '''Path: .
Working Copy Root Path: {}
URL: https://repo.com/svnroot/my_test_project/trunk
Relative URL: ^/trunk
Repository Root: https://repo.com/svnroot/my_test_project/
Repository UUID: 2d1c32hbb-f810-4327-a4d3-816543cf818f
Revision: 73465
Node Kind: directory
Schedule: normal
Last Changed Author: user1
Last Changed Rev: 73462
Last Changed Date: 2019-04-11 16:35:43 +0200 (Thu, 11 Apr 2019)
'''.format(MOCKED_REPO_LOCAL_PATH) # svn info output format of 1.7


def mock_svn_console_command(*args, **kwargs): # pylint: disable=inconsistent-return-statements
    """This mocks svn terminal command based on parameters (status, info, etc)"""
    command = args[0].split()
    if command[0] == 'svn':
        if command[1] == 'info': # pylint: disable=no-else-return
            global SVN_INFO_OUTPUT
            return SVN_INFO_OUTPUT.encode()
        elif command[1] == 'diff':
            global SVN_STATUS_OUTPUT
            return SVN_STATUS_OUTPUT.encode()
    else:
        subprocess.check_output(*args, **kwargs)


@pytest.fixture
def svn_info_erroreous_output():
    """Fixture providing mock with svn info output on error.
    Precisely, this erroreus output taken when svn 1.6 queries info on svn 1.7+ working copy"""
    global SVN_INFO_OUTPUT
    SVN_INFO_OUTPUT = '''svn: The path '{}' appears to be part of a Subversion 1.7 or greater
working copy.  Please upgrade your Subversion client to use this
working copy.
'''.format(MOCKED_REPO_LOCAL_PATH)


@pytest.fixture
def non_svn_tracked_file_svn_status():
    """Fixture providing output for svn status mock with non svn tracked file"""
    global SVN_STATUS_OUTPUT
    _svn_status_output = '''
?       {}/python_package/some_folder/test_file_two.py
'''.format(MOCKED_REPO_LOCAL_PATH)
    SVN_STATUS_OUTPUT = _svn_status_output

@pytest.fixture
def non_py_file_svn_status():
    """Fixture providing output for svn status mock with non py added file"""
    global SVN_STATUS_OUTPUT
    _svn_status_output = '''
A       {}/python_package/some_folder/some_other_data
'''.format(MOCKED_REPO_LOCAL_PATH)
    SVN_STATUS_OUTPUT = _svn_status_output

@pytest.fixture
def added_file_svn_status():
    """Fixture providing output for svn status mock with added py file"""
    global SVN_STATUS_OUTPUT
    _svn_status_output = '''
A       {}/python_package/test_file_one.py
'''.format(MOCKED_REPO_LOCAL_PATH)
    SVN_STATUS_OUTPUT = _svn_status_output


@pytest.fixture
def modified_file_svn_status():
    """Fixture providing output for svn status mock with modified py file"""
    global SVN_STATUS_OUTPUT
    _svn_status_output = '''
M       {}/python_package/test_file_one.py
'''.format(MOCKED_REPO_LOCAL_PATH)
    SVN_STATUS_OUTPUT = _svn_status_output


@pytest.fixture
def deleted_file_svn_status():
    """Fixture providing output for svn status mock with removed py file"""
    global SVN_STATUS_OUTPUT
    _svn_status_output = '''
D       {}/python_package/test_file_one.py
'''.format(MOCKED_REPO_LOCAL_PATH)
    SVN_STATUS_OUTPUT = _svn_status_output


@pytest.fixture
def file_with_multiple_tests(testdir):
    """Fixture to create a python file for linting test"""
    testdir.makepyfile(**{
        'test_ok.py': """'''A simple test'''
from __future__ import print_function


TRUE = True
assert TRUE


def test_hello_world(): # pylint: disable=missing-docstring
    print("Hello world!")


def test_assertion(number=1): # pylint: disable=missing-docstring
    assert number == 1 # pylint: disable=missing-final-newline
""",
        'test_notok.py': """import sys"""
    })



def test_basic(testdir):
    """Verify basic pylint checks"""
    testdir.makepyfile('import sys')
    result = testdir.runpytest('--pylint')
    assert 'Missing module docstring' in result.stdout.str()
    assert 'Unused import sys' in result.stdout.str()
    assert 'Final newline missing' in result.stdout.str()
    assert 'passed, ' not in result.stdout.str()
    assert '1 failed' in result.stdout.str()


def test_subdirectories(testdir):
    """Verify pylint checks files in subdirectories"""
    subdir = testdir.mkpydir('mymodule')
    testfile = subdir.join('test_file.py')
    testfile.write('import sys')
    result = testdir.runpytest('--pylint')
    assert '[pylint] mymodule/test_file.py' in result.stdout.str()
    assert 'Missing module docstring' in result.stdout.str()
    assert 'Unused import sys' in result.stdout.str()
    assert 'Final newline missing' in result.stdout.str()
    assert '1 failed' in result.stdout.str()


def test_disable(testdir):
    """Verify basic pylint checks"""
    testdir.makepyfile('import sys')
    result = testdir.runpytest('--pylint --no-pylint')
    assert 'Final newline missing' not in result.stdout.str()
    assert 'Linting files' not in result.stdout.str()


def test_pylintrc_file(testdir):
    """Verify that a specified pylint rc file will work."""
    rcfile = testdir.makefile('rc', """
[FORMAT]

max-line-length=3
""")
    testdir.makepyfile('import sys')
    result = testdir.runpytest('--pylint', '--pylint-rcfile={0}'.format(rcfile.strpath))
    assert 'Line too long (10/3)' in result.stdout.str()


def test_pylintrc_file_beside_ini(testdir):
    """
    Verify that a specified pylint rc file will work what placed into pytest ini dir.
    """
    non_cwd_dir = testdir.mkdir('non_cwd_dir')

    rcfile = non_cwd_dir.join('foo.rc')
    rcfile.write("""
[FORMAT]

max-line-length=3
""")

    inifile = non_cwd_dir.join('foo.ini')
    inifile.write("""
[pytest]
addopts = --pylint --pylint-rcfile={0}
""".format(rcfile.basename))
    pyfile = testdir.makepyfile('import sys')

    result = testdir.runpytest(
        pyfile.strpath
    )
    assert 'Line too long (10/3)' not in result.stdout.str()

    result = testdir.runpytest(
        '-c', inifile.strpath, pyfile.strpath
    )
    assert 'Line too long (10/3)' in result.stdout.str()


def test_pylintrc_ignore(testdir):
    """Verify that a pylintrc file with ignores will work."""
    rcfile = testdir.makefile('rc', """
[MASTER]

ignore = test_pylintrc_ignore.py
""")
    testdir.makepyfile('import sys')
    result = testdir.runpytest(
        '--pylint', '--pylint-rcfile={0}'.format(rcfile.strpath)
    )
    assert 'collected 0 items' in result.stdout.str()


def test_pylintrc_msg_template(testdir):
    """Verify that msg-template from pylintrc file is handled."""
    rcfile = testdir.makefile('rc', """
[REPORTS]

msg-template=start {msg_id} end
""")
    testdir.makepyfile('import sys')
    result = testdir.runpytest(
        '--pylint', '--pylint-rcfile={0}'.format(rcfile.strpath)
    )
    assert 'start W0611 end' in result.stdout.str()


def test_get_rel_path():
    """
    Verify our relative path function.
    """
    from pytest_pylint_xdist_vcs import get_rel_path  # pylint: disable=import-outside-toplevel
    correct_rel_path = 'How/Are/You/blah.py'
    path = '/Hi/How/Are/You/blah.py'
    parent_path = '/Hi/'
    assert get_rel_path(path, parent_path) == correct_rel_path

    parent_path = '/Hi'
    assert get_rel_path(path, parent_path) == correct_rel_path


def test_include_path():
    """
    Files should only be included in the list if none of the directories on
    it's path, of the filename, match an entry in the ignore list.
    """
    from pytest_pylint_xdist_vcs import include_file  # pylint: disable=import-outside-toplevel
    ignore_list = [
        'first', 'second', 'third', 'part', 'base.py'
    ]
    # Default includes.
    assert include_file('random', ignore_list) is True
    assert include_file('random/filename', ignore_list) is True
    assert include_file('random/other/filename', ignore_list) is True
    # Basic ignore matches.
    assert include_file('first/filename', ignore_list) is False
    assert include_file('random/base.py', ignore_list) is False
    # Part on paths.
    assert include_file('part/second/filename.py', ignore_list) is False
    assert include_file('random/part/filename.py', ignore_list) is False
    assert include_file('random/second/part.py', ignore_list) is False
    # Part as substring on paths.
    assert include_file('part_it/other/filename.py', ignore_list) is True
    assert include_file('random/part_it/filename.py', ignore_list) is True
    assert include_file('random/other/part_it.py', ignore_list) is True


def test_pylint_ignore_patterns():
    """Test if the ignore-patterns is working"""
    from pytest_pylint_xdist_vcs import include_file  # pylint: disable=import-outside-toplevel
    ignore_patterns = [
        'first.*',
        '.*second',
        '^third.*fourth$',
        'part',
        'base.py'
    ]

    # Default includes
    assert include_file('random', [], ignore_patterns) is True
    assert include_file('random/filename', [], ignore_patterns) is True
    assert include_file('random/other/filename', [], ignore_patterns) is True

    # Pattern matches
    assert include_file('first1', [], ignore_patterns) is False
    assert include_file('first', [], ignore_patterns) is False
    assert include_file('_second', [], ignore_patterns) is False
    assert include_file('second_', [], ignore_patterns) is False
    assert include_file('second_', [], ignore_patterns) is False
    assert include_file('third fourth', [], ignore_patterns) is False
    assert include_file('_third fourth_', [], ignore_patterns) is True
    assert include_file('part', [], ignore_patterns) is False
    assert include_file('1part2', [], ignore_patterns) is True
    assert include_file('base.py', [], ignore_patterns) is False


class TestDistributedLinting:
    """Tests related to distibuted linting with xdist"""

    @staticmethod
    def test_linting_w_xdist(testdir, file_with_multiple_tests): # pylint: disable=redefined-outer-name,unused-argument
        """Test distributed execution with pytest-xdist"""
        result = testdir.runpytest('-m', 'pylint', '--pylint', '-n=2')
        result.assert_outcomes(passed=1, failed=1)

    @staticmethod
    def test_verbose_output_during_xdist_linting(testdir, file_with_multiple_tests): # pylint: disable=redefined-outer-name,unused-argument
        """Test non verbose output during execution with pytest-xdist"""
        result = testdir.runpytest('-m', 'pylint', '--pylint', '-n=2', '-vv', '-s')
        result.stdout.re_match_lines_random([
            'scheduling tests via LoadScheduling',
            r'\[gw[0-1]\] FAILED test_notok\.py\[pylint\] <- test_notok\.py\s*',
            r'\[gw[0-1]\] PASSED test_ok\.py\[pylint\] <- test_ok\.py\s*',
        ])

    @staticmethod
    def test_non_verbose_output_during_xdist_linting(testdir, file_with_multiple_tests): # pylint: disable=redefined-outer-name,unused-argument
        """Test non verbose output during execution with pytest-xdist"""
        result = testdir.runpytest('-m', 'pylint', '--pylint', '-n=2')
        result.stdout.fnmatch_lines_random(['*gw0*', '*gw1*'])
        result.stdout.re_match_lines([r'=+ FAILURES =+', r'_+ \[pylint\] test_notok\.py _+'])

class TestVCS:
    """Tests related to VCS mode of plugin"""

    @staticmethod
    @pytest.fixture
    def testdatapath():
        """TestVCS scoped fixture to get the path to the mocked repo files"""
        return py.path.local(os.getcwd()).join('test', 'inputdata')

    @staticmethod
    def test_disable_pylint_when_vcs_mode_enabled(testdir):
        """Check pylint disable command workin in vcs mode"""
        with patch('subprocess.check_output', side_effect=mock_svn_console_command):
            result = testdir.runpytest('-vv', '-s', '-n0', '--pylint-vcs', '-m', 'pylint', '--no-pylint',
                                       MOCKED_REPO_LOCAL_PATH)
        result.stdout.fnmatch_lines('*collected 2 items / 2 deselected')
        result.assert_outcomes(passed=0, failed=0, skipped=0)

    @staticmethod
    def test_disable_vcs_mode(testdir):
        """Check if command pylint-no-vcs mode cancels vcs mode"""
        with patch('subprocess.check_output', side_effect=mock_svn_console_command):
            result = testdir.runpytest('-vv', '-s', '-n0', '--pylint-vcs', '-m', 'pylint', '--pylint-no-vcs',
                                       MOCKED_REPO_LOCAL_PATH)
        result.stdout.fnmatch_lines([
            'VCS linting mode set to disabled',
            '*test/mocked_repo/python_package/some_folder/test_file_two.py FAILED'
        ])
        assert result.parseoutcomes()['deselected'] == 2
        result.assert_outcomes(passed=2, failed=1)

    # TODO: add job to check the real files non verbose output formating

    @staticmethod
    def test_skip_lint_non_svn_file(testdir, non_svn_tracked_file_svn_status): # pylint: disable=redefined-outer-name,unused-argument
        """Test the plugin skips non vcs tracked file in vcs mode"""
        with patch('subprocess.check_output', side_effect=mock_svn_console_command):
            result = testdir.runpytest('-vv', '-s', '-n0', '--pylint-vcs', '-m', 'pylint', MOCKED_REPO_LOCAL_PATH)
        assert result.parseoutcomes() == {'deselected': 2}
        assert result.ret == ExitCode.NO_TESTS_COLLECTED

    @staticmethod
    def test_lint_added_file(testdir, added_file_svn_status): # pylint: disable=redefined-outer-name,unused-argument
        """Check linting on vcs added file"""
        with patch('subprocess.check_output', side_effect=mock_svn_console_command):
            result = testdir.runpytest('-vv', '-s', '-n0', '--pylint-vcs', '-m', 'pylint', MOCKED_REPO_LOCAL_PATH)
        result.stdout.fnmatch_lines([
            'VCS working copy detected. VCS linting mode enabled',
            '*collected 3 items / 2 deselected / 1 selected*',
            '*test/mocked_repo/python_package/test_file_one.py PASSED'
        ])
        result.assert_outcomes(passed=1)

    @staticmethod
    def test_lint_modified_file(testdir, modified_file_svn_status): # pylint: disable=redefined-outer-name,unused-argument
        """Check linting on vcs modified file"""
        with patch('subprocess.check_output', side_effect=mock_svn_console_command):
            result = testdir.runpytest('-vv', '-s', '-n0', '--pylint-vcs', '-m', 'pylint', MOCKED_REPO_LOCAL_PATH)
        result.stdout.fnmatch_lines([
            'VCS working copy detected. VCS linting mode enabled',
            '*test/mocked_repo/python_package/test_file_one.py PASSED'
        ])
        result.assert_outcomes(passed=1)

    @staticmethod
    def test_skip_lint_for_deleted_file(testdir, deleted_file_svn_status): # pylint: disable=redefined-outer-name,unused-argument
        """Check linting on vcs deleted file"""
        with patch('subprocess.check_output', side_effect=mock_svn_console_command):
            result = testdir.runpytest('-vv', '-s', '-n0', '--pylint-vcs', '-m', 'pylint', MOCKED_REPO_LOCAL_PATH)
        assert result.parseoutcomes() == {'deselected': 2}
        assert result.ret == ExitCode.NO_TESTS_COLLECTED

    @staticmethod
    def test_svn_info_internal_error(testdir, svn_info_erroreous_output): # pylint: disable=redefined-outer-name,unused-argument
        """Check linting continue if svn command error encountered"""
        with patch('subprocess.check_output', side_effect=mock_svn_console_command):
            result = testdir.runpytest('-n0', '--pylint-vcs', '-m', 'pylint', MOCKED_REPO_LOCAL_PATH)
        result.stdout.fnmatch_lines('No VCS working copy detected. VCS linting mode disabled: linting all the files')
        result.assert_outcomes(passed=2, failed=1)
