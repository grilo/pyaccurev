#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import re

import accurev.base


class Element(accurev.base.Base):

    @staticmethod
    def from_xml(client, out):
        for element in et.fromstring(out).findall('./element'):
            yield Element(client, **element.attrib)


    def __init__(self, client, **kwargs):
        super(Element, self).__init__(client, **kwargs)
        for k, v in self.__dict__.items():
            if k == '_id':
                k = '_eid'
            elif k == '_Real':
                k = '_real_version'
            elif k == '_Virtual':
                k = '_virtual_version'
            elif k == '_Loc' or k == '_location':
                k = '_location'
                if v.startswith('\\.'):
                    continue
                v = '\\'.join(v.split('/'))
                v = '\\.' + v
            setattr(self, k, v)
