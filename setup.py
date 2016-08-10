#!/usr/bin/python2
# -*- coding: utf-8 -*-
from setuptools import setup
setup(
	name='pGo-Create',
	version='01.283',
	py_modules=['pgocreate'],
	dependency_links = [
		"git+https://github.com/keyphact/pgoapi.git#egg=pgoapi",

	],
	install_requires=[
		'click',
		'colorama',
		'pgoapi',
		'lxml',
		'requests==2.10.0',
		'protobuf'
	],
	entry_points={
		'console_scripts': [
			'pgocreate = pgocreate:run'
		]
	}
)