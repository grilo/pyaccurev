#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import os

import accurev.utils
import accurev.depot


class Client:

    def __init__(self, username='biabjenkins', password='biabjenkins', server=None):
        self.username = username
        self.password = password
        self.server = server
        self.working_directory = None
        self.depots = {}

    def cmd(self, cmd):
        return accurev.utils.cmd('accurev ' + cmd, self.working_directory)

    def chdir(self, directory):
        self.working_directory = directory

    def tempfile_cmd(self, cmd, query):
        with tempfile.NamedTemporaryFile(delete=False) as text_file:
            text_file.write(query)
            text_file.close()
            rc, out, err = self.cmd(cmd + ' -l ' + text_file.name)
            os.unlink(text_file.name)
            return rc, out, err

    def xml_cmd(self, query):
        return self.tempfile_cmd('xml', query)

    def depot(self, name='ING'):
        if not name in self.depots.keys():
            self.depots[name] = accurev.depot.Depot(self, name='ING')
        return self.depots[name]

    def login(self, permanent=False):
        cmd = 'login '
        if permanent:
            cmd += '-n '
        cmd += '%s %s' % (username, password)
        return self.cmd(cmd)

    def info(self):
        rc, out, err = self.cmd('info')
        info_map = {}
        for line in out.splitlines():
            key, value = line.split(':', 1)
            key = key.lower().replace(' ', '_')
            value = value.strip()
            if value == '(none)':
                value = None
            setattr(self, key, value)
            info_map[key] = value
        return info_map

    def modify_issue(self, properties, depot='ING'):
        query = """<modifyIssue issueDB="{depot}">\n""".format(depot=depot)
        query += """\t<issue>\n"""
        for k, v in properties.items():
            query += """\t\t<{name} fid="{fid}">{value}</{name}>\n""".format(name=k, fid=v['fid'], value=v['value'])
        query += """\t<issue>\n"""
        query += """</modifyIssue>\n"""
        return self.client.xml_cmd(query)
