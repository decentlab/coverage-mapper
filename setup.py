"""setup instructions for setuptools."""

import os
from setuptools import setup, find_packages


def read(*paths):
    """Build a file path from *paths* and return the contents."""
    with open(os.path.join(*paths), 'r') as fptr:
        return fptr.read()


setup(
    name="coverage-mapper",
    version="0.1-dev",
    description="helper script to visualize coverage map",
    long_description=read("README.md"),
    classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 2.7",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    url="http://www.decentlab.com",
    author="Khash Jalsan",
    author_email="khash.jalsan@decentlab.com",
    license="Apache License 2.0",
    packages=find_packages(exclude="tests"),
    install_requires=["simplegist", "paho-mqtt",
                      "geojson", "crcmod"],
    entry_points={"console_scripts": ["cmgist = covmap.gist:main"]},
    include_package_data=True,
)
