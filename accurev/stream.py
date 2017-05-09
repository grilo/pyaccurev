#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import xml.etree.cElementTree as et

import accurev.base
import accurev.stream
import accurev.element
import accurev.issue


class ReferenceTree(accurev.base.Base):

    def __init__(self, client, **kwargs):
        super(Stream, self).__init__(client, **kwargs)
        for k, v in self.__dict__.items():
            if k == 'Loc':
                k = 'location'
            self.__dict__[k.lower()] = v


class Stream(accurev.base.Base):

    def __init__(self, client, **kwargs):
        super(Stream, self).__init__(client, **kwargs)
        self._elements = {}
        self._issues = {}
        self._children = {}
        self._refs = {}

    @property
    def elements(self):
        if len(self._elements) == 0:
            rc, out, err = self.client.cmd('stat -fexv -a -s %s' % (self._name))
            for element in et.fromstring(out).findall('./element'):
                e = accurev.element.Element(self.client, **element.attrib)
                self._elements[e.eid] = e
        return self._elements

    @property
    def workspaces(self):
        return [v for v in self.children.values() if v.type == 'workspace']

    @property
    def refs(self):
        if len(self._refs.keys()) == 0:
            rc, out, err = self.client.cmd('show -fexv refs')
            for element in et.fromstring(out).findall('./Element'):
                obj = accurev.stream.ReferenceTree(self.client, **element.attrib)
                self._refs[obj.name] = obj
        return self._refs

    @property
    def children(self):
        if len(self._children.keys()) == 0:
            rc, out, err = self.client.cmd('show -fexv -1 -s %s streams' % (self._name))
            for element in et.fromstring(out).findall('./stream'):
                if element.attrib['name'] == self._name:
                    continue
                obj = accurev.stream.Stream(self.client, **element.attrib)
                self._children[obj.name] = obj
        return self._children

    @property
    def issues(self):
        if len(self._issues.keys()) == 0:

            """
                Need to retrieve both complete and incomplete issues. Incomplete
                issues are the ones which have elements in more than one stream.
            """

            rc, out, err = self.client.cmd('issuelist -fx -s %s' % (self._name))
            for issue in et.fromstring(out).findall('./issues/issue'):
                props = {}
                for child in issue:
                    props[child.tag] = child.text
                props['stream'] = self._name
                obj = accurev.issue.Issue(self.client, **props)
                self._issues[obj.issueNum] = obj

            rc, out, err = self.client.cmd('issuelist -fx -i -s %s' % (self._name))
            for issue in et.fromstring(out).findall('./issues/issue'):
                props = {}
                for child in issue:
                    props[child.tag] = child.text
                props['stream'] = self._name
                obj = accurev.issue.Issue(self.client, **props)
                self._issues[obj.issueNum] = obj
            
        return self._issues
