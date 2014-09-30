#!/usr/bin/env python
from setuptools import setup
from vend import __version__


setup(
    name='pyvend',
    version=__version__,
    description='Thin wrapper for Vend API',
    packages=['vend'],
    keywords='vend api',
    author='Aleks Selivanov',
    author_email='aleks.selivanov@yahoo.com',
    license='BSD',
    url='http://github.com/aselivanov/pyvend',
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python'
    ]
)