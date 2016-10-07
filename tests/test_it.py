# -*- coding:utf-8 -*-
from __future__ import (
    absolute_import, division, print_function, unicode_literals
)

from django.db import connection
from django.test import TestCase


class BasicTests(TestCase):

    def test_select_1(self):
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
            assert cursor.fetchall() == ((1,),)
