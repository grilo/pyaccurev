#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import json


class Base(object):

    def __init__(self, client, **kwargs):
        for name, value in kwargs.items():
            setattr(self, '_' + name, value)
        self.client = client

    def __getattr__(self, attr):
        return self.__getattribute__(attr)

    def __getattr__(self, name):
        if '_' + name in self.__dict__.keys():
            return self.__dict__['_' + name]
        logging.debug('Available attributes: %s', [x.lstrip('_') for x in self.__dict__.keys()])
        raise ValueError('Attribute not accessible in object instance of (%s): %s' % (self.__class__.__name__, name))

    def __repr__(self):
        out = {}
        for k, v in self.__dict__.items():
            if k.startswith('_'):
                out[k.lstrip('_')] = v

        return json.dumps(out, indent=2)
