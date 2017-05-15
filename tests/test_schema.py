#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest

import accurev.mock
import accurev.client


class TestAccuRevSchema(unittest.TestCase):

    def setUp(self):
        self.schema = accurev.client.Client().depots['OFFICE'].schema

    def test_properties(self):
        expected = [
            'issueNum',
            'transNum',
            'shortDescription',
            'state',
            'JIRA',
            'lookupField',
        ]
        self.assertEqual(len(self.schema.keys()), len(expected))
