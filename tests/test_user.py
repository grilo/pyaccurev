#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest

import mock

import accurev.user
import accurev.group


class TestAccuRevUser(unittest.TestCase):

    def test_user_in_a_group(self):
        xml_user = """<?xml version="1.0" encoding="utf-8"?>
            <AcResponse
                Command="show users"
                TaskId="647018">
              <Element
                  Number="1"
                  Name="Administrator"
                  Kind="full"/>
              <Element
                  Number="2"
                  Name="PEPITO"
                  Kind="full"/>
            </AcResponse>"""

        xml_group = """<?xml version="1.0" encoding="utf-8"?>
            <AcResponse
                Command="show groups"
                TaskId="647018">
              <Element
                  Number="1"
                  Name="ADM"/>
              <Element
                  Number="2"
                  Name="AWESOME"/>
            </AcResponse>"""

        client = mock.MagicMock()
        client.group_show.return_value = xml_group
        user = list(accurev.user.User.from_xml(client, xml_user))[0]
        groups = list(user.groups)
        self.assertEquals(len(groups), 2)
        self.assertEquals(groups[0].Name, "ADM")
        self.assertEquals(groups[1].Name, "AWESOME")
