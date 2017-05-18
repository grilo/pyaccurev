#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest

import mock

import accurev.issue
#import accurev.stream


class TestAccuRevIssue(unittest.TestCase):

    def setUp(self):
        self.xml = """<?xml version="1.0" encoding="utf-8"?>
            <acResponse>
              <issues>
                <issue ancestry="direct">
                  <issueNum fid="1">101010</issueNum>
                  <transNum fid="2">4105368</transNum>
                  <shortDescription fid="3">Some fancy description</shortDescription>
                  <state fid="4">Open</state>
                  <JIRA fid="5">JIRA-10</JIRA>
                </issue>
              </issues>
            </acResponse>"""
        self.client = mock.MagicMock()
        self.issue = list(accurev.issue.Issue.from_xml(self.client, self.xml))[0]
        self.issue._depotName = 'some_depot'

    def test_issue_from_xml_returns_issue(self):
        self.assertTrue(isinstance(self.issue, accurev.issue.Issue))

    def test_lookup_field_returns_field_contents(self):
        schema = accurev.schema.Schema(None, lookupField='JIRA')
        self.client.schema.return_value = schema
        self.assertEqual(self.issue.lookupField, 'JIRA-10')

    def test_lookup_field_without_depot_defaults_to_issueNum(self):
        self.issue._depotName = None
        self.assertEqual(self.issue.lookupField, '101010')

    def test_issue_returns_stream_instance(self):
        self.client.stream_show.return_value = accurev.stream.Stream(None, name='some_stream')
        self.assertTrue(isinstance(self.issue.stream, accurev.stream.Stream))

    def test_issue_dependencies_returns_issue(self):
        client = mock.MagicMock()
        client.schema.return_value.lookupField = 'issueNum'
        self.client.cpkdepend.return_value = [accurev.issue.Issue(client, issueNum='000')]
        self.assertTrue(isinstance(self.issue.dependencies['000'], accurev.issue.Issue))

    def test_empty_dict_when_no_dependencies(self):
        self.client.cpkdepend.return_value = []
        self.assertEqual(len(self.issue.dependencies.keys()), 0)

    def test_returns_dict_with_elements(self):
        self.client.cpkdescribe.return_value = [accurev.element.Element(None, eid='100')]
        self.assertTrue(isinstance(self.issue.elements['100'], accurev.element.Element))

    def test_returns_empty_dict_without_elements(self):
        self.client.cpkdescribe.return_value = []
        self.assertEqual(len(self.issue.elements.keys()), 0)

    def test_doesnt_return_missing_elements(self):
        self.client.cpkdescribe.return_value = [accurev.element.Element(None, eid='100', missing='true')]
        self.assertEqual(len(self.issue.elements.keys()), 0)

    def test_modify_issue_no_client(self):
        self.client.modify_issue.return_value = True
        self.issue.client = None
        self.issue.shortDescription = 'some description'
        self.assertFalse(self.client.modify_issue.called)

    def test_modify_issue_no_depot(self):
        self.client.modify_issue.return_value = True
        self.issue._depotName = None
        self.issue.shortDescription = 'some description'
        self.assertFalse(self.client.modify_issue.called)

    def test_pythonic_modify_issue(self):
        self.client.schema.return_value = {
            'issueNum': {'fid': '1'},
            'transNum': {'fid': '2'},
            'shortDescription': {'fid': '3'},
        }

        self.issue.shortDescription = 'some description'
        self.client.modify_issue.assert_called_with({
            'issueNum': {
                'fid': '1',
                'value': '101010',
            },
            'shortDescription': {
                'fid': '3',
                'value': 'some description',
            }}, 'some_depot')

    def test_cpkhist_returns_transactions(self):
        t = accurev.transaction.Transaction(None, id='100')
        self.client.cpkhist.return_value = [t]
        self.assertTrue(isinstance(self.issue.hist.values()[0], \
                                   accurev.transaction.Transaction))
