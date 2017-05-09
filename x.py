#!/usr/bin/env python

import logging
logging.getLogger().setLevel(logging.DEBUG)


import accurev.client


client = accurev.client.Client()

depot = client.depot()
print 'Stream count:', len(depot.streams)

#print depot.streams['PYTHONISACORE_DEV'].workspaces
#print depot.streams['FRONT_APPS_INT'].issues

depot.streams['FRONT_APPS_INT'].issues.values()[0].developers = 'hello world'
