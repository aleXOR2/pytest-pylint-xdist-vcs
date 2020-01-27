# -*- coding: utf-8 -*-
"""Setup installation of plugin"""
from setuptools import setup


INSTALL_REQS = ['six', 'pylint']


setup(
    name='pytest-pylint-xdist-vcs',
    description='pytest plugin for multi-process linting of vcs working copy',
    python_requires='>=3',
    platforms=['linux'],
    use_scm_version={'write_to': '_version.py'},
    url='%doc% link',
    py_modules=['pytest_pylint_xdist_vcs', 'svn'],
    entry_points={'pytest11': ['pylint = pytest_pylint_xdist_vcs']},
    install_requires=INSTALL_REQS,
    setup_requires=['pytest-runner', 'setuptools_scm', 'setuptools>=24.2.0', 'pip>=9.0.0'],
    tests_require=['coverage'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: Pytest',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Testing',
    ],
)
