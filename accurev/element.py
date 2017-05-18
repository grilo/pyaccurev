#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import re
import xml.etree.cElementTree as et
import collections

import accurev.base


class Element(accurev.base.Base):

    @staticmethod
    def from_stat(client, out):
        for element in et.fromstring(out).findall('./element'):
            yield Element(client, **element.attrib)

    @staticmethod
    def from_cpkdescribe(client, out):
        """
            Returns a map containing:
                'issue_number': [

                ]
        """
        issue_elements = {}
        for issue in et.fromstring(out).findall('./issues/issue'):
            current_issue = None
            elements = {}
            for child in issue:
                if child.tag == 'issueNum':
                    current_issue = child.text
                elif child.tag == 'elements':
                    for e in child:
                        element = Element(client, **e.attrib)
                        elements[element.eid] = element
            issue_elements[current_issue] = elements
        return issue_elements

    def __init__(self, client, **kwargs):
        self._missing = None
        self._hist = collections.OrderedDict()
        super(Element, self).__init__(client, **kwargs)
        for k, v in self.__dict__.items():
            if k == '_id':
                k = '_eid'
            elif k == '_Real':
                k = '_real_version'
            elif k == '_real':
                k = '_real_version'
            elif k == '_Virtual':
                k = '_virtual_version'
            elif k == '_virtual':
                k = '_virtual_version'
            elif k == '_Loc' or k == '_location':
                k = '_location'
                if v.startswith('\\.'):
                    continue
                v = '\\'.join(v.split('/'))
                v = '\\.' + v
            setattr(self, k, v)

    @property
    def hist(self):
        if len(self._hist) == 0:
            for transaction in self.client.hist(self.eid, self.depotName):
                self._hist[transaction.id] = transaction
        return self._hist
