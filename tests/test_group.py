#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest

import mock

import accurev.user
import accurev.group


class TestAccuRevGroup(unittest.TestCase):

    def test_group_with_users(self):
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
        client.member_show.return_value = xml_user
        group = list(accurev.group.Group.from_xml(client, xml_group))[0]
        members = list(group.members)
        self.assertEquals(len(members), 2)
        self.assertEquals(members[0].Name, "Administrator")
        self.assertEquals(members[1].Name, "PEPITO")
