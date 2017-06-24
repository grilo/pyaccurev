#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import xml.etree.cElementTree as et
import collections

import accurev.utils
import accurev.base
import accurev.element


class Issue(accurev.base.Base):

    @staticmethod
    def from_xml(client, out):
        for i in et.fromstring(out).findall("./issues/issue"):
            props = {}
            for child in i:
                props[child.tag] = child.text
            yield Issue(client, **props)


    def __init__(self, client, **kwargs):
        self._stream = None
        self._depotName = None
        self._lookupField = None
        self._elements = {}
        self._hist = collections.OrderedDict()
        super(Issue, self).__init__(client, **kwargs)

    def __setattr__(self, name, value):
        """
            Implement pythonic issue modification. This enables the following
            syntax:

            depot.streams['stream_name'].issues['47'].shortDescription = 'something_else'
        """
        super(Issue, self).__setattr__(name, value)

        if not 'client' in self.__dict__.keys() or \
                self.client is None or \
                not '_depotName' in self.__dict__.keys():
            return

        schema = self.client.schema(self.depotName)
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
        if self.depotName is None:
            return self.issueNum
        else:
            field = self.client.schema(self.depotName).lookupField
            return getattr(self, field)

    @property
    def stream(self):
        return self.client.stream_show(self.depotName, self._stream)

    @property
    def dependencies(self):
        dependencies = {}
        for issue in self.client.cpkdepend([self.issueNum], \
                                            self.depotName, \
                                            self.stream.name, \
                                            self.stream.basis.name):
            issue._depotName = self.depotName
            dependencies[issue.lookupField] = issue
        return dependencies

    @property
    def elements(self):
        elements = {}
        for element in self.client.cpkdescribe([self.issueNum], self.depotName, self._stream):
            if element.missing == 'true':
                continue
            element.depotName = self.depotName
            elements[element.eid] = element
        return elements

    @property
    def hist(self):
        hist = collections.OrderedDict()
        for transaction in self.client.cpkhist([self.issueNum], self.depotName):
            hist[transaction.id] = transaction
        return hist
