#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Downloads the full tarball for the installed version of Django and runs its
test suite.
"""
from __future__ import (
    absolute_import, division, print_function, unicode_literals
)

import os
import shutil
import subprocess
import sys
from contextlib import contextmanager
from textwrap import dedent

import django
from django.utils.six.moves.urllib.request import urlopen


def main():
    if 'VIRTUAL_ENV' not in os.environ:
        print('Need to be in a virtualenv to do this', file=sys.stderr)
        return 1

    install_path = os.path.join(os.environ['VIRTUAL_ENV'], 'django_tests')
    os.makedirs(install_path)

    try:
        return run_django_tests_here(install_path)
    finally:
        shutil.rmtree(install_path)


def run_django_tests_here(install_path):
    url = 'https://github.com/django/django/archive/{}.tar.gz'.format(django.__version__)
    download_path = os.path.join(install_path, 'django.tar.gz')
    django_dir = os.path.join(install_path, 'django-{}'.format(django.__version__))

    print("Downloading full source code for Django {}".format(django.__version__))
    try:
        urlp = urlopen(url)
        with open(download_path, 'wb') as fp:
            for chunk in urlp:
                fp.write(chunk)
    finally:
        urlp.close()

    print("Extracting tarball")
    with work_in(install_path):
        ret = subprocess.call(['tar', 'xfz', 'django.tar.gz'])
    if ret:
        return ret

    print("Installing Django's test dependencies")
    test_deps_path = os.path.join(
        django_dir,
        'tests',
        'requirements',
        'py{}.txt'.format(sys.version_info[0]),
    )
    ret = subprocess.call(['pip', 'install', '-r', test_deps_path])
    if ret:
        return ret

    print("Installing custom test settings")
    test_dir = os.path.join(django_dir, 'tests')
    test_settings = os.path.join(test_dir, 'test_pymysql.py')
    with open(test_settings, 'w') as fp:
        fp.write(dedent('''\
            DATABASES = {
                'default': {
                    'ENGINE': 'django_pymysql_backend',
                },
                'other': {
                    'ENGINE': 'django_pymysql_backend',
                }
            }

            SECRET_KEY = "django_tests_secret_key"

            # Use a fast hasher to speed up tests.
            PASSWORD_HASHERS = [
                'django.contrib.auth.hashers.MD5PasswordHasher',
            ]
            '''))

    print("Running Django's test suite")
    test_file = os.path.join(test_dir, 'runtests.py')

    return subprocess.call(
        [
            sys.executable,
            test_file,
            '--settings', 'test_pymysql',
        ],
        cwd=test_dir,
    )


@contextmanager
def work_in(path):
    current = os.getcwd()
    os.chdir(path)
    yield
    os.chdir(current)


if __name__ == '__main__':
    sys.exit(main())
