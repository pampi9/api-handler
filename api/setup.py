from __future__ import print_function

import codecs
import os
import re
import sys

from setuptools import setup
from setuptools.command.test import test as test_command

here = os.path.abspath(os.path.dirname(__file__))


def read(*parts):
    # intentionally *not* adding an encoding option to open
    return codecs.open(os.path.join(here, *parts), 'r').read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


long_description = read('README.md')


class PyTest(test_command):
    def finalize_options(self):
        test_command.finalize_options(self)
        self.test_args = ['--strict', '--verbose', '--tb=long', 'tests']
        self.test_suite = True

    def run_tests(self):
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)


setup(
    name='api_handler',
    version=find_version('api', '__init__.py'),
    url='https://github.com/pampi9/api-handler.git',
    license='Apache License 2.0',
    author='Francois Boissinot',
    tests_require=['pytest'],
    install_requires=['requests', 'jsonschema', 'falcon', 'gunicorn', 'flask',
                      'flask_socketio'],
    cmdclass={'test': PyTest},
    author_email='fra.boissinot@gmail.com',
    description='Standard handling of API-calls based on OpenApi Specs in json format',
    long_description=long_description,
    entry_points={
        'console_scripts': [
            'api_ctl = api.api_ctl:run',
        ],
    },
    packages=['api', 'api.model', 'api.exceptions'],
    include_package_data=True,
    platforms='any',
    test_suite='api.tests',
    zip_safe=False,
    package_data={'api': ['schemas/**']},
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Development Status :: 4 - Beta',
        'Natural Language :: English',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    extras_require={
        'testing': ['pytest'],
    }
)
