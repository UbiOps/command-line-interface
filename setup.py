# coding: utf-8

"""
    UbiOps CLI
"""


from setuptools import setup, find_packages  # noqa: H301
from pkg.version import VERSION

NAME = "ubiops-cli"

# To install the library, run the following
#
# python setup.py install
#
# prerequisite: setuptools
# http://pypi.python.org/pypi/setuptools


def readme():
    with open('README.md') as f:
        return f.read()


ubiops_version = "3.0.0"
REQUIRES = ["urllib3>=1.15", "six>=1.10", "certifi", "requests>=2.17.3", "tabulate==0.8.7",
            "python-dateutil", "click>=7.0", "ConfigParser==4.0.2", "colorama==0.4.3", "pyyaml",
            "ubiops==%s" % ubiops_version]

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
    python_requires='>=3.5',
    packages=find_packages(where='.', exclude=['tests', 'tests.*']),
    include_package_data=True,
    entry_points='''
        [console_scripts]
        ubiops=pkg.main:main
    ''',
    project_urls={'Documentation': 'https://ubiops.com/docs',
                  'Source': 'https://github.com/UbiOps/command-line-interface.git', }
)
