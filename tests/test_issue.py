#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest

import accurev.mock
import accurev.client


class TestAccuRevDepot(unittest.TestCase):

    def setUp(self):
        self.depot = accurev.client.Client().depots['OFFICE']

    def test_has_schema(self):
        schema = self.depot.schema
        self.assertTrue(isinstance(schema, accurev.schema.Schema))
