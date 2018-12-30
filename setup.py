# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from setuptools import setup, find_packages
from os import path


here = path.abspath(path.dirname(__file__))


# Get the long description from the README file
with open(path.join(here, 'README.rst')) as f:
    long_description = f.read()


setup(
    name='Flask-WAMP',
    version='0.1.0',
    description='WAMP RPC and Pub/Sub for Flask',
    long_description=long_description,
    url='https://github.com/noisyboiler/flask-wamp',
    author='Simon Harrison',
    author_email='noisyboiler@googlemail.com',
    license='Mozilla Public License 2.0',
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='WAMP RPC Flask',
    packages=find_packages(),
    install_requires=[
        "Flask==1.0.2",
        "wampy==0.9.20",
    ],
    extras_require={
        'dev': [
            "crossbar==0.15.0",
            "autobahn==0.17.2",
            "Twisted==17.9.0",
            "pytest==4.0.2",
            "mock==1.3.0",
            "pytest-capturelog==0.7",
            "colorlog",
            "flake8==3.5.0",
            "gevent-websocket==0.10.1",
            "coverage>=3.7.1",
            "Twisted==17.9.0",
        ],
    },
)
