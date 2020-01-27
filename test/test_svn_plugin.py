"""Testing module for svn module functions"""
from unittest.mock import patch

import svn


SVN_CHANGED_FILES_OUTPUT_STUB = \
b"""
M       src/ConfigurationManagement/RadioAutomataControllerNG/StateControllers/IDeviceStateController.hpp
A       /var/fpwork/ultra_user/sub_domain_ctrl/test/py/tests/test_cases/single_core/all_systems/deployment.py
M       /var/fpwork/ultra_user/sub_domain_ctrl/test/py/tests/test_cases/single_core/all_systems/initial_transcoding.py
 M       /var/fpwork/ultra_user/sub_domain_ctrl/test/py/tests/test_cases/single_core/all_systems
D       /var/fpwork/ultra_user/sub_domain_ctrl/test/py/tests/helpers/calculations/processes.py
M       /var/fpwork/ultra_user/sub_domain_ctrl/test/py/tests/helpers/general_events.py
M       /var/fpwork/ultra_user/sub_domain_ctrl/test/py/tests/logs
M       /var/fpwork/ultra_user/sub_domain_ctrl/test/py/log
A       /var/fpwork/ultra_user/sub_domain_ctrl/test/ut/tests/ConfigurationManagement/ParamsReaderFixture.hpp
D       /var/fpwork/ultra_user/sub_domain_ctrl/test/ut/tests/ConfigurationManagement/ParamsReaderTests.cpp
"""

SVN_INFO_STUB = \
b"""
Path: /var/fpwork/ultra_user/sub_domain_ctrl
Working Copy Root Path: /var/fpwork/ultra_user/sub_domain_ctrl
URL: https://repo.de-fault.com/svnroot/sub_domain_ctrl/trunk
Relative URL: ^/trunk
Repository Root: https://repo.de-fault.com/svnroot/sub_domain_ctrl
Repository UUID: 5d1c24bb-f610-4327-a4d3-8a65489cf8183
Revision: 88160
Node Kind: directory
Schedule: normal
Last Changed Author: ultra_user
Last Changed Rev: 87892
Last Changed Date: 2019-10-11 14:47:21 +0200 (Fri, 11 Oct 2019)
"""


@patch('subprocess.check_output', return_value=SVN_CHANGED_FILES_OUTPUT_STUB)
def test_changed_filepaths_generation(checkoutput_mock): # pylint: disable=unused-argument
    """This tests ability for svn module to get all changed python files in working copy from svn info output"""
    root = '/var/fpwork/ultra_user/sub_domain_ctrl'
    lines = svn.get_mod_files(root)
    assert len(lines) == 3
    assert all(path.endswith('.py') for path in lines)


@patch('subprocess.check_output', return_value=SVN_INFO_STUB)
def test_repository_root(checkoutput_mock): # pylint: disable=unused-argument
    """This tests svn module parsing of working copy root path from svn info output"""
    path = '/var/fpwork/ultra_user/sub_domain_ctrl/test/py'
    repo_root = svn.repository_root(path)
    assert repo_root == '/var/fpwork/ultra_user/sub_domain_ctrl'
