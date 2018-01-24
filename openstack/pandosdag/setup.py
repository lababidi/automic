from setuptools import setup, find_packages

import sys
import os.path
sys.path.insert(0, os.path.abspath('.'))
from panosdag import __version__

with open('requirements.txt') as f:
    _requirements = f.read().splitlines()

with open('README.md') as f:
    _long_description = f.read()

setup(
    name='pan-os-dag',
    version=__version__,
    url='https://github.com/PaloAltoNetworks-BD/pan-os-dag',
    license='Apache',
    author='Palo Alto Networks',
    author_email='techbizdev@paloaltonetworks.com',
    description='PAN-OS OpenStack DAG',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 2.7',
        'Topic :: Security',
        'Topic :: Internet'
    ],
    long_description=_long_description,
    packages=find_packages(),
    install_requires=_requirements,
    dependency_links = [
        "git+https://github.com/openstack/python-keystoneclient.git@stable/newton#egg=python-keystoneclient",
        "git+https://github.com/openstack/python-neutronclient.git@stable/newton#egg=python-neutronclient"
    ],
    entry_points={
        'console_scripts': [
            'panosdag = panosdag.cli:main'
        ]
    }
)

