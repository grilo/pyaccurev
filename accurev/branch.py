#!/usr/bin/env python

import logging
import os
import re

import ingutils
import accurev



class Base(object):

    def __init__(self, repo, name):
        self.repo = repo
        self.name = name


class AccuRev(Base):

    def __init__(self, name, jenkins_node="0", is_release=False):
        repo = 'accurev://madprdacrv:5050/ING'
        super(AccuRev, self).__init__(repo, name)

        self.jenkins_node = jenkins_node
        self._release = is_release

        self.directory = os.path.join(os.sep + 'var', 'scm', 'accurev', 'RF_' + self.name)

        self._backing = None
        self._sandbox = None
        self._environment = None
        self._application = None
        self._exists = None
        self._fix = None

    def __repr__(self):
        return self.name

    def update(self):
        logging.info('Updating workspace: %s', self.directory)
        return ingutils.run_cmd('bash /home/jenkins/CLI/compilation/workspace-update.sh ' + self.directory, unbuffered=False, stderr=False)

    @property
    def fix(self):
        if '_FIX' in self.name:
            self._fix = True
        else:
            self._fix = False
        return self._fix

    @property
    def exists(self):
        cmd = 'accurev show -p ING -fexv -s %s streams' % (self.name)
        output = None
        xml = None
        try:
            output = ingutils.run_cmd(cmd, unbuffered=False, stderr=False, abort_on_error=False)
        except SystemExit:
            return False
        xml = et.fromstring(output).findall("./stream")
        for stream in et.fromstring(output).findall("./stream"):
            if 'name' in stream.attrib.keys():
                return True
        return False

    @property
    def backing(self):
        if self._backing is None:
            self._backing = AccuRev(accurev.get_backing_stream(self.name), self.jenkins_node, self._release)
        return self._backing

    @property
    def sandbox(self):
        if '_JENKINS_' in self.name:
            raise Exception('This branch (%s) is already a sandbox, no need to get a sandbox for a sandbox.' % (self.name))
        self._sandbox = AccuRev(self.backing.name + '_JENKINS_%s' % (self.jenkins_node), self.jenkins_node, self._release)
        if not '_JENKINS_' in self._sandbox.name:
            raise Exception('The sandbox MUST be named JENKINS (%s).', branch.sandbox.name)
        return self._sandbox

    @property
    def environment(self):
        env = None
        stream = self.name
        equivalences = {
            'LIB': 'PRO',
            'QUA': 'PRO',
            'DELIV': 'INT',
            'PRE': 'TEST',
        }

        pattern_preint = re.compile('.*(PRE.*INT).*')
        pattern_f2e = re.compile('^F2E.*TEST')
        pattern_pre = re.compile('_PRE_(DG|DA|PROFILE|MAILROOM2)')
        pattern_dbdev = re.compile('(PROFILE_DEV)')
        pattern_dbint = re.compile('(PROFILE_INT)')
        pattern_others = re.compile('.*(DEV|DELIV|INT|PRE|TEST|RC|RELEASE|_QA|QUA|PRO|LIB).*')

        if pattern_preint.search(stream):
            env = 'TEST'
        elif pattern_f2e.search(stream):
            env = 'RELEASE'
        elif pattern_pre.search(stream):
            env = 'RELEASE'
            if self._release:
                env = 'TEST'
        elif pattern_dbdev.search(stream):
            env = 'INT'
        elif pattern_dbint.search(stream):
            env = 'TEST'
        elif pattern_others.search(stream):
            env = pattern_others.match(stream).group(1)
        elif stream == 'ING_PERMISSIONS_MANAGEMENT':
            env = 'PRO'
        # If there's only one word, consider it PROduction
        elif len(re.findall(r'\w+', stream)) == 1:
            logging.debug('Defaulting to environment STOP: %s', stream)
            env = 'STOP'

        if env in equivalences.keys():
            env = equivalences[env]
        if '_FIX' in stream:
            env += '_FIX'

        if not env:
            logging.critical('Unable to guess environment for (%s)', stream)
            logging.critical('Probably a bug, contact QA team.')
            sys.exit(1)
        logging.debug('Environment for %s is: %s', stream, env)
        self._environment = env
        return self._environment

    @property
    def application(self):
        app = None
        stream = self.name
        # Ensure Jenkins suffix doesn't exist
        stream = re.sub('_JENKINS_[0-9]+', '', stream)

        # Old style ^ING... streams
        old_style_ing = re.compile('^ING_[A-Za-z0-9]+_([A-Za-z0-9]+).*')
        # BIAB streams with TEAM99 names
        dev_stream = re.compile('(.*)_[A-Za-z]+[0-9]+_DEV')
        # Fix streams
        fix_stream = re.compile('(.*)_[A-Za-z0-9]+_FIX$')
        # F2E streams
        f2e_stream = re.compile('(.*)_[A-Za-z0-9]+$')

        if old_style_ing.search(stream):
            app = old_style_ing.match(stream).group(1)
        elif dev_stream.search(stream):
            app = dev_stream.match(stream).group(1)
        elif fix_stream.search(stream):
            app = fix_stream.match(stream).group(1)
        elif f2e_stream.search(stream):
            app = f2e_stream.match(stream).group(1)

        if app == 'GENOMAFRONT':
            return 'GENOMA_FRONT'
        elif app == 'GENOMAAPI':
            return 'GENOMA_API'
        elif not app:
            logging.critical('Unknown stream format for (%s)', stream)
            logging.critical('This is probably a bug in this script, contact QA department.')
            sys.exit(1)
        self._application = app
        return self._application


if __name__ == '__main__':
    b = AccuRev('ING_DEV_ITQA')
    print b.backing
    print b.sandbox.name
    print b.environment
    print b.application
