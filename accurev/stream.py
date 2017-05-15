#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import xml.etree.cElementTree as et

import accurev.base
import accurev.stream
import accurev.element
import accurev.issue


class ReferenceTree(accurev.base.Base):

    @staticmethod
    def from_xml(client, out):
        for reftree in et.fromstring(out).findall('./Element'):
            yield accurev.stream.ReferenceTree(client, **reftree.attrib)


    def __init__(self, client, **kwargs):
        super(Stream, self).__init__(client, **kwargs)
        for k, v in self.__dict__.items():
            if k == 'Loc':
                k = 'location'
            self.__dict__[k.lower()] = v


class Stream(accurev.base.Base):

    @staticmethod
    def from_xml(client, out):
        for stream in et.fromstring(out).findall("./stream"):
            yield Stream(client, **stream.attrib)


    def __init__(self, client, **kwargs):
        self._basis = None
        self._basis_stream = None
        super(Stream, self).__init__(client, **kwargs)
        self._default_group = {}
        self._elements = {}
        self._issues = {}
        self._children = {}
        self._refs = {}
        self._family = []

    @property
    def basis(self):
        """
            Return this stream's parent <stream object>
        """
        if self._basis is None:
            return None
        elif self._basis_stream is None:
            self._basis_stream = list(self.client.stream_show(self._basis))[0]
        return self._basis_stream

    @property
    def default_group(self):
        """
            Return a map { eid : <element object> } of all elements in the
            default group (member) in this stream.
        """
        if len(self._default_group) == 0:
            for element in self.client.stream_stat(self.name, default_group=True):
                element._stream = self.name
                self._default_group[element.eid] = element
        return self._default_group

    @property
    def elements(self):
        """
            Return a map { eid : <element object> } of all elements that exist
            in this stream.
        """
        if len(self._elements) == 0:
            for element in self.client.stream_stat(self.name, default_group=True):
                element._stream = self.name
                self._elements[element.eid] = element
        return self._elements

    @property
    def workspaces(self):
        return [v for v in self.children.values() if v.type == 'workspace']

    @property
    def refs(self):
        """
            Return a map { name : <stream obj> } of all the reference trees
            associated with this stream.
        """
        if len(self._refs.keys()) == 0:
            for ref in self.client.refs_show():
                if ref.Stream != self.name:
                    continue
                self._refs[ref.name] = ref
        return self._refs

    @property
    def children(self):
        """
            Return a map { name : <stream obj> } of all the immediate children
            without including reference trees.
        """
        if len(self._children.keys()) == 0:
            for stream in accurev.client.stream_children(self.depotName, self.name):
                if stream.name == self.name:
                    continue
                self._children[stream.name] = stream
        return self._children

    @property
    def family(self):
        """
            Return a list (grandparent -> parent -> children) of <stream obj>,
            representing this stream's ancestry and all of its children. Doesn't
            include reference trees, but includes itself.
        """
        if len(self._family) == 0:
            for stream in accurev.client.stream_family(self.depotName, self.name):
                self._family.append(stream)
        return self._family

    @property
    def issues(self):
        if len(self._issues.keys()) == 0:
            for issue in self.client.stream_issues(self.depotName, self.name):
                issue._stream = self.name
                issue._depotName = self.depotName
                self._issues[issue.lookupField] = issue
        return self._issues
