#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import os

import mock

import accurev.client
import accurev.depot


class TestAccuRevClient(unittest.TestCase):

    def setUp(self):
        self.client = accurev.client.Client()

    def test_info(self):
        string = """Shell:          /bin/bash
            Principal:      automaticTasks
            Host:           madprdci2
            Domain:         (none)
            Server name:    169.0.0.1
            Port:           5050
            DB Encoding:    Unicode
            ACCUREV_BIN:    /opt/accurev-5.5/bin
            Client time:    2017/05/14 04:29:59 CEST (1494728999)
            Server time:    2017/05/14 04:30:00 CEST (1494729000)"""

        with mock.patch.object(self.client, "cmd") as mocked:
            mocked.return_value = string, ''
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
        string = """<?xml version="1.0" encoding="utf-8"?>
            <AcResponse
                Command="show depots"
                TaskId="12492">
              <Element
                  Number="1"
                  Name="OFFICE"
                  Slice="1"
                  exclusiveLocking="false"
                  case="insensitive"
                  locWidth="128"/>
              <Element
                  Number="2"
                  Name="PROVIDER"
                  Slice="2"
                  exclusiveLocking="false"
                  case="insensitive"
                  locWidth="128"/>
            </AcResponse>"""

        with mock.patch.object(self.client, "cmd") as mocked:
            mocked.return_value = string, ''
            depots = self.client.depots
            self.assertEqual(len(depots.keys()), 2)
            for d in depots.values():
                self.assertTrue(isinstance(d, accurev.depot.Depot))

    def test_login_permanent(self):
        with mock.patch.object(self.client, "cmd") as mocked:
            self.client.login('user', 'pass', permanent=True)
            mocked.assert_called_once_with('login -n user pass')

    def test_users(self):
        xml = """<?xml version="1.0" encoding="utf-8"?>
            <AcResponse
                Command="show users"
                TaskId="647018">
              <Element
                  Number="1"
                  Name="Administrator"
                  Kind="full"/>
              <Element
                  Number="2"
                  Name="SomeoneElse"
                  Kind="full"/>
            </AcResponse>"""

        with mock.patch.object(self.client, "user_show") as mocked:
            mocked.return_value = xml
            users = list(self.client.users)
            self.assertTrue(len(users), 2)

    def test_tempfile_cmd(self):
        with mock.patch.object(accurev.client.tempfile, "NamedTemporaryFile") as mocktmp:
            mocktmp.return_value = open('notrandomfile', 'w')
            with mock.patch.object(self.client, "cmd") as mocked:
                mocked.return_value = 'stdout', 'stderr'
                self.client.tempfile_cmd('xml', 'world')
                mocked.assert_called_once_with('xml -l notrandomfile')
            if os.path.isfile('notrandomfile'):
                os.unlink('notrandomfile')


    def test_group_show_no_user(self):
        with mock.patch.object(self.client, "cmd") as mocked:
            mocked.return_value = '', ''
            self.client.group_show()
            mocked.assert_called_once_with('show -fx groups')

    def test_group_show_with_user(self):
        with mock.patch.object(self.client, "cmd") as mocked:
            mocked.return_value = '', ''
            self.client.group_show('user')
            mocked.assert_called_once_with('show -fx -u user groups')

    """
    def test_member_show(self):
        with mock.patch.object(self.client, "cmd") as mocked:
            mocked.return_value = '', ''
            self.client.member_show('group')
            mocked.assert_called_once_with('show -fx -u user groups')
    """
