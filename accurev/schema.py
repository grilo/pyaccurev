#!/usr/bin/env python

import logging
import xml.etree.cElementTree as et

import accurev.base


class Schema(accurev.base.Base):

    @staticmethod
    def from_xml(client, out):
        schema = {
            'lookupField': 'issueNum',
        }

        # Get the lookup field ID
        lookupField = None
        xml_element = et.fromstring(out).findall('./lookupField')
        if xml_element:
            lookupField = xml_element[0].attrib['fid']

        for field in et.fromstring(out).findall('./field'):
            if field.attrib['fid'] == lookupField:
                schema['lookupField'] = field.attrib['name']
            schema[field.attrib['name']] = field.attrib

        return Schema(client, **schema)

    def __init__(self, client, **kwargs):
        super(Schema, self).__init__(client, **kwargs)

    @property
    def lookupField(self):
        return self._lookupField

    @property
    def fields(self):
        return self.keys()

    def values(self):
        for k, v in self.__dict__.items():
            if k != 'client' and k != '_lookupField':
                yield v
        #return [v for k, v in self.__dict__.items() if k != 'client']

    def keys(self):
        return [k for k in self.__dict__.keys() if k != 'client']
