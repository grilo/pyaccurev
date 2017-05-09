#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

import accurev.base


class Element(accurev.base.Base):

    def __init__(self, client, **kwargs):
        super(Element, self).__init__(client, **kwargs)
        for k, v in self.__dict__.items():
            if k == '_id':
                k = '_eid'
            elif k == '_Real':
                k = '_real_version'
            elif k == '_Virtual':
                k = '_virtual_version'
            setattr(self, k, v)
