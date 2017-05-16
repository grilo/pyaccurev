#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest

import mock

import accurev.stream


class TestAccuRevStream(unittest.TestCase):

    def test_basis_is_a_stream(self):
        xml = """<?xml version="1.0" encoding="utf-8"?>
            <streams>
              <stream
                  name="feature_branch_1.0"
                  basis="trunk"/>
            </streams>"""

        basis = """<?xml version="1.0" encoding="utf-8"?>
            <streams>
              <stream
                  name="trunk"/>
            </streams>"""
        client = mock.MagicMock()
        client.stream_show.return_value = accurev.stream.Stream.from_xml(None, basis)
        stream = list(accurev.stream.Stream.from_xml(client, xml))[0]
        self.assertTrue(isinstance(stream.basis, accurev.stream.Stream))

    def test_root_stream_has_no_basis(self):
        xml = """<?xml version="1.0" encoding="utf-8"?>
            <streams>
              <stream
                  name="trunk"
                  depotName="OFFICE"
                  streamNumber="1"
                  isDynamic="true"
                  type="normal"
                  startTime="1197383792"
                  hasDefaultGroup="false"/>
            </streams>"""

        basis = """<?xml version="1.0" encoding="utf-8"?>
            <streams>
              <stream
                  name="trunk"/>
            </streams>"""

        client = mock.MagicMock()
        client.stream_show.return_value = accurev.stream.Stream.from_xml(None, basis)
        stream = list(accurev.stream.Stream.from_xml(client, xml))[0]
        self.assertEqual(stream.basis, None)

    def test_default_group_returns_elements(self):
        xml = """<?xml version="1.0" encoding="utf-8"?>
            <AcResponse
                Command="stat"
                Directory="/jenkins/home/jenkins/pruebas/joaogn/pyacc"
                TaskId="302012">
              <element
                  location="/./ITQA"
                  dir="yes"
                  executable="no"
                  id="138803"
                  elemType="dir"
                  modTime="0"
                  hierType="parallel"
                  Virtual="2094/1"
                  namedVersion="ING_PRO_ITQA/1"
                  Real="32/1"
                  status="(backed)"/>
            </AcResponse>"""

        client = mock.MagicMock()
        client.stream_stat.return_value = accurev.element.Element.from_stat(None, xml)
        stream = accurev.stream.Stream(client, name='helloworld')
        element = stream.default_group['138803']
        self.assertTrue(isinstance(element, accurev.element.Element))

    def test_elements_returns_elements(self):
        xml = """<?xml version="1.0" encoding="utf-8"?>
            <AcResponse
                Command="stat"
                Directory="/jenkins/home/jenkins/pruebas/joaogn/pyacc"
                TaskId="302012">
              <element
                  location="/./ITQA"
                  dir="yes"
                  executable="no"
                  id="138803"
                  elemType="dir"
                  modTime="0"
                  hierType="parallel"
                  Virtual="2094/1"
                  namedVersion="ING_PRO_ITQA/1"
                  Real="32/1"
                  status="(backed)"/>
            </AcResponse>"""

        client = mock.MagicMock()
        client.stream_stat.return_value = accurev.element.Element.from_stat(None, xml)
        stream = accurev.stream.Stream(client, name='helloworld')
        element = stream.elements['138803']
        self.assertTrue(isinstance(element, accurev.element.Element))

    def test_elements_adds_stream_name(self):
        xml = """<?xml version="1.0" encoding="utf-8"?>
            <AcResponse
                Command="stat"
                Directory="/jenkins/home/jenkins/pruebas/joaogn/pyacc"
                TaskId="302012">
              <element
                  location="/./ITQA"
                  dir="yes"
                  executable="no"
                  id="138803"
                  Virtual="2094/1"
                  namedVersion="ING_PRO_ITQA/1"
                  Real="32/1"
                  status="(backed)"/>
            </AcResponse>"""

        client = mock.MagicMock()
        client.stream_stat.return_value = accurev.element.Element.from_stat(None, xml)
        stream = accurev.stream.Stream(client, name='helloworld')
        element = stream.elements['138803']
        self.assertTrue(element.stream, 'helloworld')

    def test_stream_children_doesnt_return_itself(self):
        xml = """<?xml version="1.0" encoding="utf-8"?>
            <streams>
              <stream name="helloworld"/>
              <stream name="some_child"/>
            </streams>"""

        client = mock.MagicMock()
        client.stream_children.return_value = accurev.stream.Stream.from_xml(None, xml)
        stream = accurev.stream.Stream(client, name='helloworld', depotName='doesntmatter')
        self.assertEqual(len(stream.children), 1)
        self.assertEqual(stream.children.values()[0].name, 'some_child')

    def test_stream_workspaces(self):
        xml = """<?xml version="1.0" encoding="utf-8"?>
            <streams>
              <stream
                type="snapshot"
                name="stream1"/>
              <stream
                type="normal"
                name="stream2"/>
              <stream
                type="workspace"
                name="stream3"/>
            </streams>"""

        client = mock.MagicMock()
        client.stream_children.return_value = accurev.stream.Stream.from_xml(None, xml)
        stream = accurev.stream.Stream(client, name='helloworld', depotName='doesntmatter')
        self.assertEqual(len(stream.workspaces), 1)
        self.assertEqual(stream.workspaces.values()[0].name, 'stream3')

    def test_stream_workspaces(self):

        xml = """<?xml version="1.0" encoding="utf-8"?>
            <streams>
              <stream
                type="snapshot"
                name="stream1"/>
              <stream
                type="normal"
                name="stream2"/>
              <stream
                type="workspace"
                name="stream3"/>
            </streams>"""

        client = mock.MagicMock()
        client.stream_children.return_value = accurev.stream.Stream.from_xml(None, xml)
        stream = accurev.stream.Stream(client, name='helloworld', depotName='doesntmatter')
        self.assertEqual(len(stream.workspaces), 1)
        self.assertEqual(stream.workspaces.values()[0].name, 'stream3')

    def test_stream_family(self):

        xml = """<?xml version="1.0" encoding="utf-8"?>
            <streams>
              <stream
                type="normal"
                name="parent1"/>
              <stream
                type="normal"
                name="helloworld"/>
              <stream
                type="workspace"
                name="child1"/>
            </streams>"""

        client = mock.MagicMock()
        client.stream_family.return_value = accurev.stream.Stream.from_xml(None, xml)
        stream = accurev.stream.Stream(client, name='helloworld', depotName='doesntmatter')
        self.assertEqual(len(stream.family), 3)


    def test_stream_issues_returns_issues(self):
        xml = """<?xml version="1.0" encoding="utf-8"?>
            <acResponse>
              <issues>
                <issue ancestry="direct">
                  <issueNum fid="1">101010</issueNum>
                  <transNum fid="2">4105368</transNum>
                  <shortDescription fid="3">Some fancy description</shortDescription>
                  <state fid="4">Open</state>
                  <JIRA fid="5">JIRA-10</JIRA>
                </issue>
                <issue ancestry="direct">
                  <issueNum fid="1">202020</issueNum>
                  <transNum fid="2">4106525</transNum>
                  <shortDescription fid="3">Another Fancy Description</shortDescription>
                  <state fid="4">Closed</state>
                  <JIRA fid="5">JIRA-20</JIRA>
                </issue>
              </issues>
            </acResponse>"""

        schema = """<?xml version="1.0" encoding="UTF-8"?>
            <template name="default">
                <lookupField fid="5"/>
                <field name="issueNum" fid="5"></field>
            </template>"""

        client = mock.MagicMock()
        client.schema.return_value = accurev.schema.Schema.from_xml(None, schema)
        client.stream_issues.return_value = accurev.issue.Issue.from_xml(client, xml)
        stream = accurev.stream.Stream(client, name='helloworld', depotName='doesntmatter')
        self.assertEqual(len(stream.issues), 2)
        for issue in stream.issues.values():
            self.assertTrue(isinstance(issue, accurev.issue.Issue))

    def test_stream_reference_trees(self):
        xml = """<?xml version="1.0" encoding="utf-8"?>
            <AcResponse
                Command="show refs"
                TaskId="316705">
              <Element
                  Name="reftree_one"
                  Storage="E:/RefTree/reftree_one"
                  Host="hostname"
                  Type="3"
                  user_id="1"
                  Stream="20"
                  user_name="Administrator"/>
              <Element
                  Name="reftree_two"
                  Storage="E:/RefTree/reftree_two"
                  Host="hostname"
                  Type="3"
                  user_id="1"
                  Stream="21"
                  user_name="Administrator"/>
            </AcResponse>"""

        client = mock.MagicMock()
        client.refs_show.return_value = accurev.stream.ReferenceTree.from_xml(None, xml)
        stream = accurev.stream.Stream(client, name='helloworld', depotName='doesntmatter', streamNumber="20")
        self.assertEqual(len(stream.refs), 1)
        for ref in stream.refs.values():
            self.assertTrue(isinstance(ref, accurev.stream.ReferenceTree))
