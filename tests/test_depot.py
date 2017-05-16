#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest

import mock

import accurev.depot
import accurev.schema
import accurev.stream


class TestAccuRevDepot(unittest.TestCase):

    def test_depot_from_xml(self):
        xml = """<?xml version="1.0" encoding="utf-8"?>
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

        depots = list(accurev.depot.Depot.from_xml(None, xml))
        self.assertEqual(len(depots), 2)

    def test_depot_from_xml_attributes(self):
        xml = """<?xml version="1.0" encoding="utf-8"?>
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
            </AcResponse>"""
        depot = list(accurev.depot.Depot.from_xml(None, xml))[0]
        for k in ['number', 'name']:
            self.assertTrue(isinstance(getattr(depot, k), str))
        self.assertTrue

    def test_has_schema(self):
        xml = """<?xml version="1.0" encoding="utf-8"?>
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
            </AcResponse>"""

        schema = """<?xml version="1.0" encoding="UTF-8"?>
            <template name="default">
                <lookupField fid="5"/>
                <field name="issueNum" fid="5"></field>
            </template>"""

        client = mock.MagicMock()
        client.schema.return_value = accurev.schema.Schema.from_xml(None, schema)
        depot = list(accurev.depot.Depot.from_xml(client, xml))[0]
        self.assertTrue(isinstance(depot.schema, accurev.schema.Schema))

    def test_has_streams(self):
        xml = """<?xml version="1.0" encoding="utf-8"?>
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
            </AcResponse>"""

        stream_xml = """<streams>
                  <stream
                      name="trunk"
                      depotName="OFFICE"
                      streamNumber="1"
                      isDynamic="true"
                      type="normal"
                      startTime="1197383792"
                      hasDefaultGroup="false"/>
                  <stream
                      name="feature_branch_1.0"
                      basis="trunk"
                      basisStreamNumber="1"
                      depotName="OFFICE"
                      streamNumber="2"
                      isDynamic="true"
                      type="normal"
                      startTime="1413204397"
                      hasDefaultGroup="true"/>
            </streams>"""

        client = mock.MagicMock()
        client.stream_show.return_value = accurev.stream.Stream.from_xml(None, stream_xml)
        depot = list(accurev.depot.Depot.from_xml(client, xml))[0]
        self.assertEqual(len(depot.streams.keys()), 2)
        for stream in depot.streams.values():
            self.assertTrue(isinstance(stream, accurev.stream.Stream))
