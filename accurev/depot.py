#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import xml.etree.cElementTree as et

import accurev.base
import accurev.stream


class Depot(accurev.base.Base):

    def __init__(self, client, **kwargs):
        super(Depot, self).__init__(client, **kwargs)
        self._issues = {}
        self._streams = {}

    @property
    def streams(self):
        if len(self._streams.keys()) == 0:
            rc, out, err = self.client.cmd('show -p %s -fxg streams' % (self._name))
            for stream in et.fromstring(out).findall("./stream"):
                if stream.attrib['type'] == 'workspace':    
                    continue
                self._streams[stream.attrib['name']] = accurev.stream.Stream(self.client, **stream.attrib)
        return self._streams
