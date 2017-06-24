#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import xml.etree.cElementTree as et

import accurev.base
import accurev.group


class User(accurev.base.Base):

    @staticmethod
    def from_xml(client, out):
        for depot in et.fromstring(out).findall('./Element'):
            yield User(client, **depot.attrib)


    def __init__(self, client, **kwargs):
        super(User, self).__init__(client, **kwargs)
        for k, v in self.__dict__.items():
            self.__dict__[k.lower()] = v

    @property
    def groups(self):
        return accurev.group.Group.from_xml(self.client, self.client.group_show(self.name))
