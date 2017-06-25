#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import os
import collections

import mock

import accurev.client
import accurev.depot


class TestAccuRevClient(unittest.TestCase):

    def setUp(self):
        self.client = accurev.client.Client()

    def test_cmd(self):
        self.client.chdir('somedirectory')
        expected = "accurev somecommand"

        with mock.patch.object(accurev.utils, "cmd") as mocked:
            self.client.cmd('somecommand')
            mocked.assert_called_once_with('accurev somecommand', 'somedirectory')

    def test_xml_cmd(self):
        with mock.patch.object(self.client, "tempfile_cmd") as mocked:
            self.client.xml_cmd('somestring')
            mocked.assert_called_once_with('xml', 'somestring')

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

    def test_member_show(self):
        with mock.patch.object(self.client, "cmd") as mocked:
            mocked.return_value = '', ''
            self.client.member_show('group')
            mocked.assert_called_once_with('show -fx -g group members')

    def test_cpkdescribe(self):

        query = "<AcRequest>\n"
        query += "\t<cpkdescribe>\n"
        query += "\t\t<depot>mycompany</depot>\n"
        query += "\t\t<stream1>some_stream</stream1>\n"
        query += "\t\t<issues>\n"
        query += "\t\t\t<issueNum>1010</issueNum>\n"
        query += "\t\t</issues>\n"
        query += "\t</cpkdescribe>\n"
        query += "</AcRequest>"

        response = """<?xml version="1.0" encoding="utf-8"?>
            <acResponse>
              <issues>
                <issue ancestry="direct">
                  <issueNum fid="1">1010</issueNum>
                </issue>
              </issues>
            </acResponse>"""

        with mock.patch.object(self.client, "xml_cmd") as mocked:
            mocked.return_value = response, ''
            issues = self.client.cpkdescribe(['1010'], 'mycompany', 'some_stream')
            mocked.assert_called_once_with(query)

    def test_schema(self):
        response = """<?xml version="1.0" encoding="UTF-8"?>
        <template name="default">
            <lookupField fid="5"/>
            <field name="issueNum" type="internal" label="Issue" reportWidth="10" fid="1"></field>
            <field name="transNum" type="internal" label="Transaction" reportWidth="10" fid="2"> </field>
            <field name="shortDescription" type="Text" label="Short Description" reportWidth="150" width="60" fid="3"></field>
            <field name="state" type="Choose" label="State" reportWidth="10" fid="4">
                <value>Open</value>
                <value>Cancelled</value>
                <value>Closed</value>
            </field>
            <field name="JIRA" type="Text" label="Jira Issue" reportWidth="10" width="15" fid="5"></field>
        </template>"""

        with mock.patch.object(self.client, "getconfig") as mocked:
            mocked.return_value = response, ''
            schema = self.client.schema('mycompany')
            mocked.assert_called_once_with('mycompany', 'schema.xml')

    def test_element_promote(self):

        response = "<elements>\n"
        response += """\t<e eid="10" v="1/1"/>\n"""
        response += """\t<e eid="11" v="2/2"/>\n"""
        response += "</elements>"

        class Element:
            pass

        element_one = Element()
        element_one.eid = "10"
        element_one.real_version = "1/1"

        element_two = Element()
        element_two.eid = "11"
        element_two.real_version ="2/2"

        element_list = [
            element_one,
            element_two
        ]

        with mock.patch.object(self.client, "tempfile_cmd") as mocked:
            self.client.element_promote(element_list, 'hello', 'world')
            mocked.assert_called_once_with('promote -s hello -S world -Fx', response)

    def test_issue_query(self):

        expected = """<queryIssue issueDB="mycompany" useAltQuery="false">\n"""
        expected += "\t<OR>\n"
        expected += "\t\t<condition>1 == 10</condition>\n"
        expected += "\t\t<condition>1 == 20</condition>\n"
        expected += "\t</OR>\n"
        expected += "</queryIssue>"

        response = """<?something>\n"""
        response += """<issueOne/>"""
        response += """<issueTwo/>"""

        with mock.patch.object(self.client, "xml_cmd") as mocked:
            mocked.return_value = response, ''
            out, err = self.client.issue_query('mycompany', ['10', '20'])
            mocked.assert_called_once_with(expected)

    def test_stream_show(self):
        response = """<?xml version="1.0" encoding="utf-8"?>
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

        with mock.patch.object(self.client, "cmd") as mocked:
            mocked.return_value = response, ''
            self.client.stream_show('mycompany', 'trunk')
            mocked.assert_called_once_with('show -p mycompany -fxg -s trunk streams')

    def test_stream_children(self):
        response = """<?xml version="1.0" encoding="utf-8"?>
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

        with mock.patch.object(self.client, "cmd") as mocked:
            mocked.return_value = response, ''
            self.client.stream_children('mycompany', 'trunk')
            mocked.assert_called_once_with('show -p mycompany -fexvg -1 -s trunk streams')

    def test_stream_family(self):
        response = """<?xml version="1.0" encoding="utf-8"?>
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

        with mock.patch.object(self.client, "cmd") as mocked:
            mocked.return_value = response, ''
            self.client.stream_family('mycompany', 'trunk')
            mocked.assert_called_once_with('show -p mycompany -fexvg -r -s trunk streams')


    def test_stream_issues(self):
        expected = [
            'issuelist -p mycompany -fx -s some_stream',
            'issuelist -p mycompany -fx -s some_stream -i',
        ]
        response = """<?xml version="1.0" encoding="utf-8"?>
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

        with mock.patch.object(self.client, "cmd") as mocked:
            mocked.return_value = response, ''
            # Ensure we prime the generator, otherwise nosetests won't consider
            # the method as executed.
            issues = list(self.client.stream_issues('mycompany', 'some_stream'))
            for e in expected:
                mocked.assert_any_call(e)


    def test_stream_stat_default_group(self):

        response = """<?xml version="1.0" encoding="utf-8"?>
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

        with mock.patch.object(self.client, "cmd") as mocked:
            mocked.return_value = response, ''
            elements = list(self.client.stream_stat('some_stream', default_group=True))
            mocked.assert_called_once_with('stat -fexv -s some_stream -d')

    def test_stream_stat_all(self):

        response = """<?xml version="1.0" encoding="utf-8"?>
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

        with mock.patch.object(self.client, "cmd") as mocked:
            mocked.return_value = response, ''
            elements = list(self.client.stream_stat('some_stream', default_group=False))
            mocked.assert_called_once_with('stat -fexv -s some_stream -a')

    def test_modify_issue(self):

        expected = """<modifyIssue issueDB="mycompany">\n"""
        expected += "\t<issue>\n"
        expected += """\t\t<one fid="1">1</one>\n"""
        expected += """\t\t<two fid="2">2</two>\n"""
        expected += "\t</issue>\n"
        expected += "</modifyIssue>\n"

        properties = collections.OrderedDict()
        properties['one'] = {
            'fid': '1',
            'value': '1',
        }
        properties['two'] = {
            'fid': '2',
            'value': '2',
        }

        with mock.patch.object(self.client, "xml_cmd") as mocked:
            mocked.return_value = '', ''
            result = self.client.modify_issue(properties, 'mycompany')
            mocked.assert_called_once_with(expected)

    def test_cpkhist(self):

        expected = '<acRequest>\n'
        expected += '\t<cpkhist verbose="true">\n'
        expected += '\t\t<depot>mycompany</depot>\n'
        expected += '\t\t<issues>\n'
        expected += '\t\t\t<issue>\n'
        expected += '\t\t\t\t<issueNum>1</issueNum>\n'
        expected += '\t\t\t</issue>\n'
        expected += '\t\t\t<issue>\n'
        expected += '\t\t\t\t<issueNum>2</issueNum>\n'
        expected += '\t\t\t</issue>\n'
        expected += '\t\t</issues>\n'
        expected += '\t</cpkhist>\n'
        expected += '</acRequest>'

        with mock.patch.object(self.client, "xml_cmd") as mocked:
            mocked.return_value = '', ''
            result = self.client.cpkhist(['1', '2'], 'mycompany')
            mocked.assert_called_once_with(expected)

    def test_issue_promote(self):

        expected = '<issues>\n'
        expected += '\t<id>1</id>\n'
        expected += '\t<id>2</id>\n'
        expected += '</issues>'

        with mock.patch.object(self.client, "tempfile_cmd") as mocked:
            self.client.issue_promote(['1', '2'], 'source', 'target')
            mocked.assert_called_once_with('promote -s source -S target -Fx', expected)

    def test_default_group_promote(self):
        with mock.patch.object(self.client, "cmd") as mocked:
            self.client.default_group_promote('source', 'target')
            mocked.assert_called_once_with('promote -s source -S target -d')

    def test_refs_show(self):
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
            </AcResponse>"""

        with mock.patch.object(self.client, "cmd") as mocked:
            mocked.return_value = xml, ''
            self.client.refs_show()
            mocked.assert_called_once_with('show -fexv refs')

    def test_hist(self):

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
                </transaction>
              </element>
            </AcResponse>"""

        with mock.patch.object(self.client, "cmd") as mocked:
            mocked.return_value = xml, ''
            self.client.hist('100', 'mycompany')
            mocked.assert_called_once_with('hist -fexv -p mycompany -e 100')

    def test_cpkdepend(self):

        xml = """<?xml version="1.0" encoding="utf-8"?>
            <AcResponse
                Command="cpkdepend"
                TaskId="646546">
                <issueDependencies>
                    <issueDependency>
                        <dependencies>
                            <issue number="10"/>
                        </dependencies>
                    </issueDependency>
                </issueDependencies>
            </AcResponse>"""

        response = """<?something>\n"""
        response += """<issueOne/>"""
        response += """<issueTwo/>"""

        with mock.patch.object(self.client, "cmd") as mocked_cmd:
            mocked_cmd.return_value = xml, ''

            with mock.patch.object(self.client, "issue_query") as mocked_query:
                mocked_query.return_value = response, ''
                self.client.cpkdepend(['10', '20'], 'mycompany', 'source', 'target')
                mocked_cmd.assert_called_once_with('cpkdepend -fvx -p mycompany -s source -S target -I 10,20')
