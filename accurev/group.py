#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import xml.etree.cElementTree as et

import accurev.base
import accurev.user


class Group(accurev.base.Base):

    @staticmethod
    def from_xml(client, out):
        for depot in et.fromstring(out).findall('./Element'):
            yield Group(client, **depot.attrib)


    def __init__(self, client, **kwargs):
        super(Group, self).__init__(client, **kwargs)
        for k, v in self.__dict__.items():
            self.__dict__[k.lower()] = v

    @property
    def members(self):
        return accurev.user.User.from_xml(self.client, self.client.member_show(self.name))
