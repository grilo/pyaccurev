#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
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
        for k, v in self.__dict__.items():
            self.__dict__[k.lower()] = v

    @property
    def schema(self):
        return self.client.schema(self._Name)

    @property
    def streams(self):
        streams = {}
        for stream in self.client.stream_show(self._Name):
            streams[stream.name] = stream
        return streams
