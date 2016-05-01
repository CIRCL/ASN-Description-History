#!/usr/bin/python
# -*- coding: utf-8 -*-
from setuptools import setup

setup(
    name='asnhistory',
    version='2.0',
    description='Query a redis database to access to the ASNs descriptions.',
    url='https://github.com/Rafiot/ASN-Description-History',
    author='Raphaël Vinot',
    author_email='raphael.vinot@circl.lu',
    maintainer='Raphaël Vinot',
    maintainer_email='raphael.vinot@circl.lu',
    packages=['asnhistory'],
    classifiers=[
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Telecommunications Industry',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Topic :: Security',
        'Topic :: Internet',
    ],
    long_description=open('README.md').read(),
    install_requires=['redis', 'dateutils'],
)
