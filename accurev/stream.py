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
        super(ReferenceTree, self).__init__(client, **kwargs)


class Stream(accurev.base.Base):

    @staticmethod
    def from_xml(client, out):
        for stream in et.fromstring(out).findall("./stream"):
            yield Stream(client, **stream.attrib)


    def __init__(self, client, **kwargs):
        self._basis = None
        self._basis_stream = None
        super(Stream, self).__init__(client, **kwargs)

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
        default_group = {}
        for element in self.elements.values():
            if 'member' in element.status:
                default_group[element.eid] = element
        return default_group

    @property
    def elements(self):
        """
            Return a map { eid : <element object> } of all elements that exist
            in this stream.
        """
        elements = {}
        for element in self.client.stream_stat(self.name):
            element._stream = self.name
            element._depotName = self.depotName
            elements[element.eid] = element
        return elements

    @property
    def children(self):
        """
            Return a map { name : <stream obj> } of all the immediate children
            without including reference trees.
        """
        children = {}
        for stream in self.client.stream_children(self.depotName, self.name):
            if stream.name == self.name:
                continue
            children[stream.name] = stream
        return children

    @property
    def workspaces(self):
        workspaces = {}
        for name, stream in self.children.items():
            if stream.type == 'workspace':
                workspaces[name] = stream
        return workspaces

    @property
    def family(self):
        """
            Return a list (grandparent -> parent -> children) of <stream obj>,
            representing this stream's ancestry and all of its children. Doesn't
            include reference trees, but includes itself.
        """
        family = []
        for stream in self.client.stream_family(self.depotName, self.name):
            family.append(stream)
        return family

    @property
    def issues(self):
        issues = {}
        for issue in self.client.stream_issues(self.depotName, self.name):
            issue._stream = self.name
            issue._depotName = self.depotName
            issues[issue.lookupField] = issue
        return issues

    @property
    def refs(self):
        """
            Return a map { name : <stream obj> } of all the reference trees
            associated with this stream.
        """
        refs = {}
        for ref in self.client.refs_show():
            if ref.Stream != self.streamNumber:
                continue
            refs[ref.Name] = ref
        return refs
