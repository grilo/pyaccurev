#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest

import mock

import accurev.utils


class TestAccuRevClient(unittest.TestCase):

    def test_error_command(self):
        result = None
        out, err = ('', '')
        try:
            accurev.utils.cmd('ls', '/doesntexist')
        except OSError:
            result = True
        self.assertTrue(result)

    def test_stdout(self):
        out, err = accurev.utils.cmd('echo "hello"')
        self.assertEqual(out, 'hello\n')
        self.assertEqual(err, '')
