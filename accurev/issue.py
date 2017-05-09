#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import xml.etree.cElementTree as et

import accurev.base


class Issue(accurev.base.Base):

    def __init__(self, client, **kwargs):
        super(Issue, self).__init__(client, **kwargs)
        self._elements = {}

    def __setattr__(self, name, value):
        super(Issue, self).__setattr__(name, value)
        schema = self._get_db_schema()
        if not name in schema.keys():
            return

        props = {}

        for k, v in schema.items():
            if k == 'transNum':
                continue
            elif k == name:
                props[k] = {
                    'fid': v['fid'],
                    'value': value,
                }
            elif '_' + k in self.__dict__.keys():
                props[k] = {
                    'fid': v['fid'],
                    'value': self.__dict__['_' + k],
                }

        rc, out, err = self.client.modify_issue(props)
        if rc != 0:
            raise Exception(err)

#    my $meta = @{get_issue_meta(\@issue)}[0];
#    my $schema = utils::get_db_schema();
#
#    my $query = "<modifyIssue issueDB=\"ING\">\n";
#    $query .= "\t<issue>\n";
#
#    foreach my $k (keys %{$schema}) {
#        $k eq "transNum" and next;
#        if ($k eq $key) {
#            $query .= "\t\t<$k fid=\"$schema->{$k}\">$value</$k>\n";
#        } elsif (exists ($meta->{$k})) {
#            $query .= "\t\t<$k fid=\"$schema->{$k}\">$meta->{$k}[0]->{'content'}</$k>\n";
#        }
#        # Else, adding fields with empty values to the CR just means they'll be ignored
#    }
#
#    $query .= "\t</issue>\n";
#    $query .= "</modifyIssue>\n";
#
#    my $response = utils::xml_query($query);
#    if ($?) {
#        die("Error modifying CR: $query\n");
#    }
#
        

    def _get_db_schema(self):
        """
            AccuRev actually supports multiple templates for the issues, alas
            there's no support for it in the implementation below.
        """
        rc, out, err = self.client.cmd('getconfig -p ING -r schema.xml')
        schema = {}
        for field in et.fromstring(out).findall('./field'):
            schema[field.attrib['name']] = field.attrib
        return schema            

#<?xml version="1.0" encoding="UTF-8"?>
#<template name="default">
#<lookupField fid="34"/>
#<field
#name="issueNum"
#type="internal"
#label="Issue"
#reportWidth="10"
#fid="1">
#</field>
#<field
#name="transNum"
#type="internal"
#label="Transaction"
#reportWidth="10"
#fid="2">
#</field>

#sub get_db_schema {
#    my $schema;
#    my $response = `accurev getconfig -p ING -r schema.xml`;
#    $response = XML::Simple::XMLin($response, ForceArray => 1, KeyAttr => '');
#    foreach my $field (@{$response->{'field'}}) {
#        $schema->{$field->{'name'}} = $field->{'fid'};
#    }
#    return $schema;
#}

#    my $meta = @{get_issue_meta(\@issue)}[0];
#    my $schema = utils::get_db_schema();
#
#    my $query = "<modifyIssue issueDB=\"ING\">\n";
#    $query .= "\t<issue>\n";
#
#    foreach my $k (keys %{$schema}) {
#        $k eq "transNum" and next;
#        if ($k eq $key) {
#            $query .= "\t\t<$k fid=\"$schema->{$k}\">$value</$k>\n";
#        } elsif (exists ($meta->{$k})) {
#            $query .= "\t\t<$k fid=\"$schema->{$k}\">$meta->{$k}[0]->{'content'}</$k>\n";
#        }
#        # Else, adding fields with empty values to the CR just means they'll be ignored
#    }
#
#    $query .= "\t</issue>\n";
#    $query .= "</modifyIssue>\n";
#
#    my $response = utils::xml_query($query);
#    if ($?) {
#        die("Error modifying CR: $query\n");
#    }
#


#def get_issue_elements(issues, stream=None):
#    logging.debug("Get issue elements: %s :: %s", str(issues), stream)
#    elements = {}
#    for i in issues:
#        elements[i] = []
#
#    if len(elements.keys()) == 0:
#        return elements
#
#    query = "<AcRequest><cpkdescribe><depot>ING</depot>"
#    if stream:
#        query += "<stream1>%s</stream1>" % (stream)
#    query += "<issues>"
#    for i in issues:
#        query += "<issueNum>%s</issueNum>" % (str(i))
#    query += "</issues></cpkdescribe></AcRequest>"
#
#    root = et.fromstring(xml_cmd(query))
#    for node in root.findall('./issues/issue'):
#        issueNum = node.find('issueNum').text
#        elements[issueNum] = []
#        for e in node.find('./elements'):
#            e = e.attrib
#            e['eid'] = e['id']
#            e['version'] = e['real_version']
#            if not 'missing' in e.keys():
#                e['missing'] = 'false'
#            if not 'overlap' in e.keys():
#                e['overlap'] = 'false'
#            elements[issueNum].append(e)
#    return elements
#
