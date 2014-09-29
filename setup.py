#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""This setup script packages pyblish_maya"""

from setuptools import setup, find_packages


with open('README.txt') as f:
    readme = f.read()


import os
import imp

version_file = os.path.abspath('pyblish_maya/version.py')
version_mod = imp.load_source('version', version_file)
version = version_mod.version


classifiers = [
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.6',
    'Programming Language :: Python :: 2.7',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'Topic :: Utilities'
]


setup(
    name='pyblish-maya',
    version=version,
    packages=find_packages(),
    package_dir={'pyblish': 'pyblish'},
    url='https://github.com/abstractfactory/pyblish-maya',
    license='LGPL',
    author='Abstract Factory and Contributors',
    author_email='marcus@abstractfactory.io',
    description='Maya integration of Pyblish',
    long_description=readme,
    zip_safe=False,
    classifiers=classifiers,
    package_data={
        'pyblish_maya': ['plugins/*.py',
                         'pythonpath/*.py']
    },
)
