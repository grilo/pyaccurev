#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest

import accurev.mock
import accurev.client


class TestAccuRevStream(unittest.TestCase):

    def setUp(self):
        self.streams = accurev.client.Client().depots['OFFICE'].streams

    def test_stream_contain_depot_name(self):
        for s in self.streams.values():
            self.assertTrue(isinstance(s.depotName, str))

    def test_basis_is_a_stream(self):
        stream = self.streams['feature_branch_1.0']
        self.assertTrue(isinstance(stream.basis, accurev.stream.Stream))

    def test_root_stream_has_no_basis(self):
        stream = self.streams['trunk']
        self.assertEqual(stream.basis, None)
