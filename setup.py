from setuptools import setup

UBIOPS_VERSION = "4.8.0"

DEPENDENCIES=[
    "requests>=2.17.3",
    "tabulate==0.8.10",
    "python-dateutil",
    "click>=7.0,<8.0",
    "ConfigParser==4.0.2",
    "colorama==0.4.3",
    "pyyaml",
    f"ubiops=={UBIOPS_VERSION}",
]

setup(
    name="ubiops-cli",
    install_requires=DEPENDENCIES,
)
