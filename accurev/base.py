#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import json


class Base(object):

    def __init__(self, client, **kwargs):
        self.client = client
        for name, value in kwargs.items():
            setattr(self, '_' + name, value)

    def __getattr__(self, name):
        for k in self.__dict__.keys():
            if name == k.lstrip('_'):
                return self.__dict__[k]

    def __repr__(self):
        out = {}
        for k, v in self.__dict__.items():
            if k.startswith('_'):
                out[k.lstrip('_')] = v
        
        return json.dumps(out, indent=2)
