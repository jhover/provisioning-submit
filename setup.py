#!/usr/bin/env python
#
# Setup prog for Certify certificate management utility

import sys
from distutils.core import setup

setup(
    name="provisioning-submit",
    version='0.9.0',
    description='Utilities for submitting and configuring VMs.',
    long_description='''Utilities for submitting and configuring VMs.''',
    license='GPL',
    author='John Hover',
    author_email='jhover@bnl.gov',
    url='https://www.racf.bnl.gov/experiments/usatlas/griddev/',
    packages=[ 'provisioning',
              ],
    classifiers=[
          'Development Status :: 3 - Beta',
          'Environment :: Console',
          'Intended Audience :: System Administrators',
          'License :: OSI Approved :: GPL',
          'Operating System :: POSIX',
          'Programming Language :: Python',
          'Topic :: System Administration :: Management',
    ],
    scripts=[ 'bin/generate-userdata',

             ],
    data_files=[ ('share/provisioning', ['README.txt', 'LGPL.txt', ] ) ],
)

