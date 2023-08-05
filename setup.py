# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

# get version from __version__ variable in jammy_app/__init__.py
from jammy_app import __version__ as version


with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

setup(
	name='jammy_app',
	version=version,
	description='Jammy',
	author='GreyCube',
	author_email='admin@greycube.in',
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
