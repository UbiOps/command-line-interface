# coding: utf-8

"""
    UbiOps CLI
"""


from setuptools import setup, find_packages  # noqa: H301
from ubiops_cli.version import VERSION

NAME = "ubiops-cli"

# To install the library, run the following
#
# python setup.py install
#
# prerequisite: setuptools
# http://pypi.python.org/pypi/setuptools


def readme():
    """
    Return README content
    """

    return """
Command Line Interface to interact with the UbiOps API (v2.1).

Read the documentation at: https://github.com/UbiOps/command-line-interface

More information about UbiOps: https://ubiops.com/

UbiOps-cli is compatible with Python 3.7+ and is distributed under the Apache 2.0 License.
"""


UBIOPS_VERSION = "4.7.0"
REQUIRES = [
    "requests>=2.17.3",
    "tabulate==0.8.10",
    "python-dateutil",
    "click>=7.0,<8.0",
    "ConfigParser==4.0.2",
    "colorama==0.4.3",
    "pyyaml",
    f"ubiops=={UBIOPS_VERSION}"
]

setup(
    name=NAME,
    version=VERSION,
    description="UbiOps Command Line Interface to interact with the UbiOps API. ",
    author="UbiOps",
    url="https://github.com/UbiOps/command-line-interface.git",
    keywords=["UbiOps Command Line Interface"],
    classifiers=['Development Status :: 3 - Alpha',
                 'License :: OSI Approved :: Apache Software License',
                 'Programming Language :: Python :: 3 :: Only',
                 'Intended Audience :: Developers'],
    license='Apache 2.0',
    long_description_content_type='text/markdown',
    long_description=readme(),
    install_requires=REQUIRES,
    python_requires='>=3.7',
    packages=find_packages(where='.', exclude=['tests', 'tests.*']),
    include_package_data=True,
    entry_points='''
        [console_scripts]
        ubiops=ubiops_cli.main:main
    ''',
    project_urls={'Documentation': 'https://ubiops.com/docs',
                  'Source': 'https://github.com/UbiOps/command-line-interface.git', }
)
