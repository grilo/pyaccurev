#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import xml.etree.cElementTree as et

import accurev.utils
import accurev.base
import accurev.element


class Issue(accurev.base.Base):

    @staticmethod
    def from_xml(client, out):
        issues = []
        for i in et.fromstring(out).findall("./issues/issue"):
            props = {}
            for child in i:
                props[child.tag] = child.text
            yield Issue(client, **props)


    def __init__(self, client, **kwargs):
        self._stream = None
        self._lookupField = None
        super(Issue, self).__init__(client, **kwargs)
        self._elements = {}
        self._dependencies = {}

    def __setattr__(self, name, value):
        """
            Implement pythonic issue modification. This enables the following
            syntax: 

            depot.streams['stream_name'].issues['47'].shortDescription = 'something_else'
        """
        super(Issue, self).__setattr__(name, value)

        if not 'client' in self.__dict__.keys() or not 'depotName' in self.__dict__.keys():
            return

        schema = self.client.depot_schema(self.depotName)
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

        return self.client.modify_issue(props, self.depotName)

    @property
    def lookupField(self):
        return self.__dict__[self.client.depot_schema(self.depotName).lookupId]

    @property
    def stream(self):
        return accurev.stream.Stream.from_name(self.client, self.depotName, self._stream)

    @property
    def dependencies(self):
        if len(self._dependencies) == 0:
            for issue in self.client.cpkdepend([self.issueNum], self.depotName, self.stream.name, self.stream.basis.name):
                issue._depotName = self.depotName
                self._dependencies[issue.lookupField] = issue
        return self._dependencies

    @property
    def elements(self):
        if len(self._elements.keys()) == 0:
            rc, out, err = self.client.cpkdescribe([self.issueNum], self.depotName, self._stream)
            for element in et.fromstring(out).findall('./issues/issue/elements/element'):
                if element.attrib['missing'] == 'true':
                    continue
                element.attrib['issue'] = self.issueNum
                e = accurev.element.Element(self.client, **element.attrib)
                self._elements[e.eid] = e
        return self._elements
