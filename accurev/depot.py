#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import xml.etree.ElementTree as xet
import xml.etree.cElementTree as et

import accurev.base
import accurev.stream
import accurev.schema


class Depot(accurev.base.Base):

    @staticmethod
    def from_xml(client, out):
        for depot in et.fromstring(out).findall('./Element'):
            yield Depot(client, **depot.attrib)


    def __init__(self, client, **kwargs):
        super(Depot, self).__init__(client, **kwargs)
        self._issues = {}
        self._streams = {}
        self._schema = None
        for k, v in self.__dict__.items():
            self.__dict__[k.lower()] = v

    @property
    def schema(self):
        if self._schema is None:
            self._schema = self.client.schema(self._Name)
        return self._schema

    @property
    def streams(self):
        if len(self._streams.keys()) == 0:
            for stream in self.client.stream_show(self._Name):
                self._streams[stream.name] = stream
        return self._streams
