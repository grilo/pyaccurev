#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

import accurev


class ReferenceTree(accurev.Base):

    def __init__(self, client, **kwargs):
        super(Workspace, self).__init__(client, kwargs)
        self.elements = {}
