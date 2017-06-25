#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest

import mock

import accurev.base


class TestAccuRevClient(unittest.TestCase):

    def setUp(self):
        client = mock.Mock()
        properties = {
            'key': 'value',
            'anotherkey': 'anothervalue',
        }
        self.base = accurev.base.Base(client, **properties)


    def test_init(self):
        self.assertEqual(self.base._key, 'value')
        self.assertEqual(self.base._anotherkey, 'anothervalue')

    def test_getattr_doesnt_exist(self):
        result = None
        try:
            self.base.doesnt_exist
        except ValueError:
            result = True
        self.assertTrue(result)

    def test_repr(self):
        expected = """{\n  "anotherkey": "anothervalue", \n  "key": "value"\n}"""
        result = self.base.__repr__()
        self.assertEqual(result, expected)
