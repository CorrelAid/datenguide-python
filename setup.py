#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open("README.rst") as readme_file:
    readme = readme_file.read()

with open("HISTORY.rst") as history_file:
    history = history_file.read()

requirements = ["pandas>=0.25.0", "requests"]

setup_requirements = ["pytest-runner"]

test_requirements = ["pytest"]

setup(
    name="datenguidepy",
    version="0.1.2",
    packages=find_packages(include=["datenguidepy"]),
    author="CorrelAid",
    author_email="packages@correlaid.org",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Other Audience",
        "Intended Audience :: Science/Research",
        "Natural Language :: English",
        "Natural Language :: German",
        "Operating System :: OS Independent",
        "Topic :: Education",
        "Topic :: Sociology",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    description=(
        "Provids easy access to German " + "publically availible regional statistics"
    ),
    install_requires=requirements,
    license="MIT license",
    long_description=readme + "\n\n" + history,
    include_package_data=True,
    keywords="datenguidepy",
    setup_requires=setup_requirements,
    test_suite="tests",
    tests_require=test_requirements,
    url="https://github.com/CorrelAid/datenguide-python",
    zip_safe=False,
)
