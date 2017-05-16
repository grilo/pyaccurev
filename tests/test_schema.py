#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest

import mock

import accurev.schema


class TestAccuRevSchema(unittest.TestCase):

    def setUp(self):
        xml = """<?xml version="1.0" encoding="UTF-8"?>
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

        self.schema = accurev.schema.Schema.from_xml(None, xml)

    def test_from_xml_returns_schema(self):
        self.assertTrue(isinstance(self.schema, accurev.schema.Schema))

    def test_schema_contains_all_properties(self):
        expected = [
            'issueNum',
            'transNum',
            'shortDescription',
            'state',
            'JIRA',
        ]

        self.assertTrue(len(self.schema.fields), 5)
        self.assertTrue(len(self.schema.keys()), 5)

    def test_schema_values_returns_dict_of_properties(self):
        for value in self.schema.values():
            self.assertTrue(isinstance(value, dict))

        self.assertEqual(self.schema.issueNum['type'], 'internal')
        self.assertEqual(self.schema.issueNum['label'], 'Issue')
        self.assertEqual(self.schema.issueNum['reportWidth'], '10')
        self.assertEqual(self.schema.issueNum['fid'], '1')

    def test_schema_lookup_field_matches_input(self):
        self.assertEqual(self.schema.lookupField, 'JIRA')

    def test_schema_lookup_field_defaults_to_issueNum(self):
        xml = """<?xml version="1.0" encoding="UTF-8"?>
        <template name="default">
            <field name="issueNum" type="internal" label="Issue" reportWidth="10" fid="1"></field>
            <field name="JIRA" type="Text" label="Jira Issue" reportWidth="10" width="15" fid="5"></field>
        </template>"""
        schema = accurev.schema.Schema.from_xml(None, xml)
        self.assertEqual(schema.lookupField, 'issueNum')
