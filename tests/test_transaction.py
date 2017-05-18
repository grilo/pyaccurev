#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest

import mock

import accurev.transaction


class TestAccuRevTransaction(unittest.TestCase):

    def test_transaction_from_cpkhist(self):
        xml = """<?xml version="1.0" encoding="utf-8"?>
            <acResponse>
              <transaction
                  id="50"
                  type="dispatch"
                  time="1495016042"
                  user="JohnDoe"
                  cpk="remove">
                <issues>
                  <issue>
                    <issueNum>52545</issueNum>
                    <JIRA>10</JIRA>
                    <elements>
                      <element
                          eid="101010"
                          member="0"
                          name="/some/file/path"/>
                    </elements>
                  </issue>
                </issues>
              </transaction>
            </acResponse>"""

        t = list(accurev.transaction.Transaction.from_cpkhist(None, xml))[0]
        self.assertTrue(isinstance(t, accurev.transaction.Transaction))
        self.assertEqual(t.id, '50')
        self.assertEqual(t.type, 'dispatch')
        self.assertEqual(t.elements.keys(), ['101010'])


    def test_transaction_from_hist(self):
        xml = """<?xml version="1.0" encoding="utf-8"?>
            <AcResponse
                Command="hist"
                TaskId="646546">
              <element
                  id="100">
                <transaction
                    id="2020"
                    type="promote"
                    time="1495051170"
                    user="JohnDoe"
                    streamName="StreamDestination"
                    streamNumber="13638"
                    fromStreamName="StreamOrigin"
                    fromStreamNumber="13752">
                  <comment>A nice comment</comment>
                  <version
                      path="/some/path"
                      eid="90"
                      virtual="13638/2"
                      real="18125/1"
                      virtualNamedVersion="StreamDestination/2"
                      realNamedVersion="UserWorkspace/1"
                      elem_type="text"
                      dir="no">
                    <issueNum>50</issueNum>
                  </version>
                  <comment>Another nice comment.</comment>
                  <version
                      path="/path/to/another/file"
                      eid="91"
                      virtual="18125/1"
                      real="18125/1"
                      virtualNamedVersion="UserWorkspace/1"
                      realNamedVersion="UserWorkspace/1"
                      ancestor="21498/3"
                      ancestorNamedVersion="ParentUserWorkspace/3"
                      elem_type="text"
                      dir="no"
                      mtime="1494943451"
                      cksum="855249265"
                      sz="861">
                    <issueNum>50</issueNum>
                  </version>
                </transaction>
              </element>
            </AcResponse>"""

        t = list(accurev.transaction.Transaction.from_hist(None, xml))[0]
        self.assertTrue(isinstance(t, accurev.transaction.Transaction))
        self.assertEqual(t.id, '2020')
        self.assertEqual(t.type, 'promote')
        self.assertTrue('90' in t.elements.keys())
        self.assertTrue('91' in t.elements.keys())
