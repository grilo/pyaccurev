#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest

import accurev.mock
import accurev.client
import accurev.depot


class TestAccuRevClient(unittest.TestCase):

    def setUp(self):
        self.client = accurev.client.Client()

    def test_info(self):
        self.assertTrue(isinstance(self.client.info, dict))
        expected = [
            'Shell',
            'Principal',
            'Host',
            'Domain',
            'Server name',
            'Port',
            'DB Encoding',
            'ACCUREV_BIN',
            'Client time',
            'Server time',
        ]
        self.assertEqual(len(self.client.info.keys()), len(expected))

    def test_depot_count(self):
        self.assertEqual(len(self.client.depots.keys()), 2)

    def test_depot_instance(self):
        for d in self.client.depots.values():
            self.assertTrue(isinstance(d, accurev.depot.Depot))

    def test_login_permanent(self):
        out, err = self.client.login()
        self.assertEqual(out, '')
        self.assertEqual(err, '')
