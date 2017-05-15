#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import cPickle
import os
import subprocess
import shlex


class Memoize(object):
    def __init__(self, function):
        self.function = function
        self.memo = {}
    def __call__(self, *args, **kwds):
        string = cPickle.dumps(args, 1) + cPickle.dumps(kwds, 1)
        if not self.memo.has_key(string): # Cache miss
            self.memo[string] = self.function(*args, **kwds)
        else: # Cache hit
            pass
        return self.memo[string]

@Memoize
def cmd(command, directory=None):
    logging.debug(command)
    old_dir = os.getcwd()
    if directory:
        os.chdir(directory)

    p = subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    rc = p.returncode

    if directory:
        os.chdir(old_dir)

    if rc != 0:
        logging.critical('Command return code: %i', rc)
        logging.critical('STDOUT: %s', out)
        logging.critical('STDERR: %s', err)
        raise OSError(rc)

    return out, err
