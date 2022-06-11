#!/usr/bin/python3

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='EEI',
    version='0.1',
    description='SPD Excel Parser',
    url='https://github.com/linuxyz/spd-parser.git',
    author='linuxyz',
    author_email='linuxyz@users.noreply.github.com',
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: LGPL-2.1 License",
        "Operating System :: OS Independent",
    ],
)
