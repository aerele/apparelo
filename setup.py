# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

with open('requirements.txt') as f:
	install_requires = f.read().strip().split('\n')

# get version from __version__ variable in apparelo/__init__.py
from apparelo import __version__ as version

setup(
	name='apparelo',
	version=version,
	description='Frappe application to manage the manufacturing workflows in the garment industry.',
	author='Aerele Technologies Private Limited',
	author_email='apparelo@aerele.in',
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
