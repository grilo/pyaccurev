#!/usr/bin/env python

import logging
logging.getLogger().setLevel(logging.DEBUG)

import accurev.client
import accurev.mock

client = accurev.client.Client()

print 'Stream count:', len(client.depots['OFFICE'].streams)

for stream in client.depots['OFFICE'].streams:
    print stream

print client.depots['OFFICE'].streams['feature_branch_2.0']


#print depot.streams['PYTHONISACORE_DEV'].workspaces
#print depot.streams['FRONT_APPS_INT'].issues

#depot.streams['FRONT_APPS_INT'].issues.values()[0].developers = 'YT81UA'

#print depot.streams['FRONT_APPS_INT'].issues.values()[0]

#print client.depots
#print client.depots['ING']
#print client.depots['ING'].streams

#for e in client.depots['ING'].streams['FRONT_APPS_INT'].issues['STRY0025612'].elements.values():
#    if e.missing == "false":
#        print e

# Promote by issue
#for issue in client.depots['ING'].streams['FRONT_APPS_IMPGEN1_DEV'].issues.values():
#    if issue.IDNotes == 'STRY0028181':
#        out, err = client.promote_issues([issue.issueNum], issue.stream.name, 'FRONT_APPS_INT_JENKINS_0')
#        print out

#for dependency in client.depots['ING'].streams['FRONT_APPS_INT'].issues['STRY0025612'].dependencies.values():
#    print dependency

#for dependency in client.depots['ING'].streams['FRONT_APPS_INT'].issues['STRY0025612'].dependencies.values():
#    print dependency
