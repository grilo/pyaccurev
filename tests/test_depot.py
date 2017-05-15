#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest

import accurev.mock
import accurev.client
import accurev.depot
import accurev.schema


class TestAccuRevDepot(unittest.TestCase):

    def setUp(self):
        self.depot = accurev.client.Client().depots['OFFICE']

    def test_has_schema(self):
        schema = self.depot.schema
        self.assertTrue(isinstance(schema, accurev.schema.Schema))

    def test_contains_streams(self):
        streams = self.depot.streams
        self.assertTrue(len(streams.keys()) > 0)