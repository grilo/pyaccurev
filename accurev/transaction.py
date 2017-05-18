#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import re
import xml.etree.cElementTree as et
import collections

import accurev.base
import accurev.element


class Transaction(accurev.base.Base):

    @staticmethod
    def from_hist(client, out):
        for transaction in et.fromstring(out).findall('./element/transaction'):
            t = Transaction(client, **transaction.attrib)
            version_pairs = []
            for child in transaction:
                if child.tag == 'comment':
                    version_pairs.append((child.text, {}))
                elif child.tag == 'version':
                    for k, v in child.attrib.items():
                        version_pairs[-1][-1][k] = v
                        version_pairs[-1][-1]['issueNum'] = []
                    for issue in child.findall('./issueNum'):
                        version_pairs[-1][-1]['issueNum'].append(issue.text)
            for comment, version in version_pairs:
                version['comment'] = comment
                t.elements[version['eid']] = version
            yield t

    @staticmethod
    def from_cpkhist(client, out):
        for transaction in et.fromstring(out).findall('./transaction'):
            t = Transaction(client, **transaction.attrib)
            for element in transaction.findall('./issues/issue/elements/element'):
                e = accurev.element.Element(client, **element.attrib)
                t.elements[e.eid] = e
            yield t

    def __init__(self, client, **kwargs):
        self._versions = collections.OrderedDict()
        self._elements = {}
        super(Transaction, self).__init__(client, **kwargs)
