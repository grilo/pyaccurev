#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import os
import tempfile
import xml.etree.cElementTree as et

import accurev.utils
import accurev.depot
import accurev.schema


class Client:

    def __init__(self, username='biabjenkins', password='biabjenkins', server=None):
        self.username = username
        self.password = password
        self.server = server
        self.working_directory = None
        self._depots = {}
        self._info = {}

    def __repr__(self):
        return self.info

    def chdir(self, directory):
        self.working_directory = directory

    def cmd(self, cmd):
        return accurev.utils.cmd('accurev ' + cmd, self.working_directory)

    def tempfile_cmd(self, cmd, query):
        with tempfile.NamedTemporaryFile(delete=False) as text_file:
            text_file.write(query)
            text_file.close()
            out, err = self.cmd(cmd + ' -l ' + text_file.name)
            os.unlink(text_file.name)
            return out, err

    def xml_cmd(self, query):
        return self.tempfile_cmd('xml', query)

    @property
    def depots(self):
        if len(self._depots.keys()) == 0:
            out, err = self.cmd('show -fx depots')
            for depot in accurev.depot.Depot.from_xml(self, out):
                self._depots[depot.Name] = depot
        return self._depots

    @property
    def info(self):
        if len(self._info.keys()) == 0:
            out, err = self.cmd('info')
            for line in out.splitlines():
                key, value = line.split(':', 1)
                key = key.lower().replace(' ', '_')
                value = value.strip()
                if value == '(none)':
                    value = None
                setattr(self, key, value)
                self._info[key] = value
        return self._info

    def login(self, permanent=False):
        cmd = 'login '
        if permanent:
            cmd += '-n '
        cmd += '%s %s' % (self.username, self.password)
        return self.cmd(cmd)

    def modify_issue(self, properties, depot):
        query = """<modifyIssue issueDB="{depot}">\n""".format(depot=depot)
        query += '\t<issue>\n'
        for k, v in properties.items():
            query += """\t\t<{name} fid="{fid}">{value}</{name}>\n""".format(name=k, fid=v['fid'], value=v['value'])
        query += '\t</issue>\n'
        query += '</modifyIssue>\n'
        return self.xml_cmd(query)

    def cpkdescribe(self, issues, depot, stream=None):
        assert isinstance(issues, list)

        query = '<AcRequest>\n'
        query += '\t<cpkdescribe>\n'
        query += '\t\t<depot>{depot}</depot>\n'.format(depot=depot)
        if stream:
            query += '\t\t<stream1>{stream}</stream1>\n'.format(stream=stream)
        query += '\t\t<issues>'
        for i in issues:
            query += '\t\t\t<issueNum>{issue}</issueNum>\n'.format(issue=i)
        query += '\t\t</issues>\n'
        query += '\t</cpkdescribe>\n'
        query += '</AcRequest>'

        out, err = self.xml_cmd(query)
        return accurev.element.Element.from_cpkdescribe(out)

    def getconfig(self, config_name, depot):
        cmd = 'getconfig -p {depot} -r {config_name}'.format(depot=depot, config_name=config_name)
        return self.cmd(cmd)

    def schema(self, depot):
        out, err = self.getconfig(depot, 'schema.xml')
        return accurev.schema.Schema.from_xml(self, out)

    def cpkdepend(self, issues, depot, source_stream, target_stream=None):
        cmd = 'cpkdepend -fvx -p {depot} -s {source_stream} -S {target_stream} -I {issues}'.format(depot=depot, source_stream=source_stream, target_stream=target_stream, issues=','.join(issues))
        out, err = self.cmd(cmd)
        issues = []
        for i in et.fromstring(out).findall('./issueDependencies/issueDependency/dependencies/issue'):
            issues.append(i.attrib['number'])

        out, err = self.issue_query(depot, issues)
        for issue in accurev.issue.Issue.from_xml(self, out):
            yield issue

    def element_promote(self, element_list, source_stream, target_stream):
        query = '<elements>\n'
        for element in element_list:
            query += """\t<e eid="{eid}" v="{real_version}"/>\n""".format(eid=element.eid, real_version=element.real_version)
        query += '</elements>'
        cmd = 'promote -s {source_stream} -S {target_stream} -Fx'.format(source_stream=source_stream, target_stream=target_stream)
        return self.tempfile_cmd(cmd, query)

    def issue_promote(self, issue_list, source_stream, target_stream):
        query = '<issues>\n'
        for issue in issue_list:
            query += '\t<id>{issue}</id>\n'.format(issue=issue)
        query += '</issues>'
        cmd = 'promote -s {source_stream} -S {target_stream} -Fx'.format(source_stream=source_stream, target_stream=target_stream)
        return self.tempfile_cmd(cmd, query)

    def default_group_promote(self, source_stream, target_stream):
        cmd = 'promote -s {source_stream} -S {target_stream} -d'.format(source_stream=source_stream, target_stream=target_stream)
        return self.cmd(cmd)

    def issue_query(self, depot, issue_list):
        query = """<queryIssue issueDB="{depot}" useAltQuery="false">\n""".format(depot=depot)
        query += '\t<OR>\n'
        for i in issue_list:
            query += '\t\t<condition>1 == {issue}</condition>\n'.format(issue=str(i))
        query += '\t</OR>\n'
        query += '</queryIssue>'
        out, err = self.xml_cmd(query)
        # Because accurev's output is horrible inconsistent...
        out = out.split('\n')
        out.insert(1, '<acResponse>')
        out.append('</acResponse>')
        return out, err

    def stream_show(self, depot, stream=None):
        # 'stream' also works with a number
        cmd = 'show -p {depot} -fxg'.format(depot=depot)
        if not stream is None:
            cmd += ' -s {stream}'.format(stream=stream)
        cmd += ' streams'
        out, err = self.cmd(cmd)
        for stream in accurev.stream.Stream.from_xml(self, out):
            yield stream

    def stream_children(self, depot, stream):
        cmd = 'show -p {depot} -fexvg -1 -s {stream} streams'.format(depot=depot, stream=stream)
        out, err = self.cmd(cmd)
        for stream in accurev.stream.Stream.from_xml(self, out):
            yield stream

    def stream_family(self, depot, stream):
        cmd = 'show -p {depot} -fexvg -r -s {stream} streams'.format(depot=depot, stream=stream)
        out, err = self.cmd(cmd)
        for stream in accurev.stream.Stream.from_xml(self, out):
            yield stream

    def stream_issues(self, depot, stream):
        """
            Need to retrieve both complete and incomplete issues. Incomplete
            issues are the ones which have elements in more than one stream.
        """
        commands = [
            'issuelist -p {depot} -fx -s {stream}'.format(depot=depot, stream=stream),
            'issuelist -p {depot} -fx -s {stream} -i'.format(depot=depot, stream=stream),
        ]

        for cmd in commands:
            out, err = self.cmd(cmd)
            for issue in accurev.issue.Issue.from_xml(self, out):
                yield issue

    def stream_stat(self, stream, default_group=False):
        cmd = 'stat -fexv -s {stream}'.format(stream=stream)
        if default_group:
            cmd += ' -d'
        else:
            cmd += ' -a'
        out, err = self.cmd('stat -fexv -d -s %s' % (self.name))
        for element in accurev.element.Element.from_stat(self, out):
            yield element

    def refs_show(self):
        out, err = self.cmd('show -fexv refs')
        for reftree in accurev.stream.ReferenceTree.from_xml(out):
            yield reftree

    def cpkhist(self, issues, depot):
        assert isinstance(issues, list)

        query = '<acRequest>\n'
        query += '\t<cpkhist verbose="true">\n'
        query += '\t\t<depot>{depot}</depot>\n'.format(depot=depot)
        query += '\t\t<issues>'
        for i in issues:
            query += '\t\t\t<issue>\n'
            query += '\t\t\t\t<issueNum>{issue}</issueNum>\n'.format(issue=i)
            query += '\t\t\t</issue>\n'
        query += '\t\t</issues>\n'
        query += '\t</cpkhist>\n'
        query += '</acRequest>'

        out, err = self.xml_cmd(query)
        for transaction in accurev.transaction.Transaction.from_cpkhist(self, out):
            yield transaction

    def hist(self, eid, depot):
        cmd = 'hist -fexv -p {depot} -e {eid}'.format(depot=depot, eid=eid)
        out, err = self.cmd('stat -fexv -d -s %s' % (self.name))
        for transaction in accurev.transaction.Transaction(self, out):
            yield transaction
