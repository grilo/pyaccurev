#!/usr/bin/env python

import logging
import types

import accurev.client


accurev_info = """Shell:          /bin/bash
Principal:      automaticTasks
Host:           madprdci2
Domain:         (none)
Server name:    169.0.0.1
Port:           5050
DB Encoding:    Unicode
ACCUREV_BIN:    /opt/accurev-5.5/bin
Client time:    2017/05/14 04:29:59 CEST (1494728999)
Server time:    2017/05/14 04:30:00 CEST (1494729000)"""

schema = """<?xml version="1.0" encoding="UTF-8"?>
<template name="default">
    <lookupField fid="5"/>
    <field name="issueNum" type="internal" label="Issue" reportWidth="10" fid="1"></field>
    <field name="transNum" type="internal" label="Transaction" reportWidth="10" fid="2"> </field>
    <field name="shortDescription" type="Text" label="Short Description" reportWidth="150" width="60" fid="3"></field>
    <field name="state" type="Choose" label="State" reportWidth="10" fid="4">
        <value>Open</value>
        <value>Cancelled</value>
        <value>Closed</value>
    </field>
    <field name="JIRA" type="Text" label="Jira Issue" reportWidth="10" width="15" fid="5"></field>
</template>"""

issuelist = """<?xml version="1.0" encoding="utf-8"?>
<acResponse>
  <issues>   
    <issue ancestry="direct">
      <issueNum fid="1">101010</issueNum>
      <transNum fid="2">4105368</transNum>
      <shortDescription fid="3">Some fancy description</shortDescription>
      <state fid="4">Open</state>
      <JIRA fid="5">JIRA-10</state>
    </issue>
    <issue ancestry="direct">
      <issueNum fid="1">202020</issueNum>
      <transNum fid="2">4106525</transNum>
      <shortDescription fid="3">Another Fancy Description</shortDescription>
      <state fid="4">Closed</state>
      <JIRA fid="5">JIRA-20</state>
    </issue>
  </issues>
</acResponse>"""

issuelist_i = """<?xml version="1.0" encoding="utf-8"?>
<acResponse>
  <issues>   
    <issue ancestry="direct">
      <issueNum fid="1">303030</issueNum>
      <transNum fid="2">4105368</transNum>
      <shortDescription fid="3">More fancy description</shortDescription>
      <state fid="4">Open</state>
      <JIRA fid="5">JIRA-30</state>
    </issue>
    <issue ancestry="direct">
      <issueNum fid="1">303030</issueNum>
      <transNum fid="2">4105368</transNum>
      <shortDescription fid="3">Some more fancy description</shortDescription>
      <state fid="4">Cancelled</state>
      <JIRA fid="5">JIRA-40</state>
    </issue>
  </issues>
</acResponse>"""

show_depots = """<?xml version="1.0" encoding="utf-8"?>
<AcResponse
    Command="show depots"
    TaskId="12492">
  <Element
      Number="1"
      Name="OFFICE"
      Slice="1"
      exclusiveLocking="false"
      case="insensitive"
      locWidth="128"/>
  <Element
      Number="2"
      Name="PROVIDER"
      Slice="2"
      exclusiveLocking="false"
      case="insensitive"
      locWidth="128"/>
</AcResponse>"""

show_streams_office = """<?xml version="1.0" encoding="utf-8"?>
<streams>
  <stream
      name="trunk"
      depotName="OFFICE"
      streamNumber="1"
      isDynamic="true"
      type="normal"
      startTime="1197383792"
      hasDefaultGroup="false"/>
  <stream
      name="feature_branch_1.0"
      basis="trunk"
      basisStreamNumber="1"
      depotName="OFFICE"
      streamNumber="2"
      isDynamic="true"
      type="normal"
      startTime="1413204397"
      hasDefaultGroup="true"/>
  <stream
      name="feature_branch_2.0"
      basis="feature_branch_1.0"
      basisStreamNumber="2"
      depotName="OFFICE"
      streamNumber="3"
      isDynamic="true"
      type="snapshot"
      startTime="1413204397"
      hasDefaultGroup="true"/>
  <stream
      name="Workspace_John_Doe.0"
      basis="feature_branch_2.0"
      basisStreamNumber="3"
      depotName="OFFICE"
      streamNumber="4"
      isDynamic="true"
      type="workspace"
      startTime="1413204397"
      hasDefaultGroup="true"/>
</streams>"""
show_streams_trunk = """<?xml version="1.0" encoding="utf-8"?>
<streams>
  <stream
      name="trunk"
      depotName="OFFICE"
      streamNumber="1"
      isDynamic="true"
      type="normal"
      startTime="1197383792"
      hasDefaultGroup="false"/>
</streams>"""

show_streams_fb1 = """<?xml version="1.0" encoding="utf-8"?>
<streams>
  <stream
      name="feature_branch_1.0"
      basis="trunk"
      basisStreamNumber="1"
      depotName="OFFICE"
      streamNumber="2"
      isDynamic="true"
      type="normal"
      startTime="1413204397"
      hasDefaultGroup="true"/>
</streams>"""

def cmd(self, command):
    logging.debug('MOCK: [%s]', command)
    rc = 0
    out = None
    err = ''


    if command == 'show -fx depots':
        out = show_depots
    elif command == 'show -p trunk -fxg streams':
        out = show_streams_trunk
    elif command == 'show -p feature_branch_1.0 -fxg streams':
        out = show_streams_fb1
    elif command == 'info':
        out = accurev_info
        err = 'You are not in a directory associated with a workspace'
    elif command.startswith('login'):
        out = ''
    elif 'schema.xml' in command:
        out = schema

    elif command.startswith('issuelist'):
        if ' -i' in command:
            out = issuelist_i
        out = issuelist
    elif command.startswith('show'):
        if ' streams' in command:
            if ' -p OFFICE' in command:
                out = show_streams_office
    #logging.debug('MOCK: [output]:\n%s', out)
    if out is None:
        logging.critical('MOCK: missing implementation for: %s', command)
    return out, err

print 'Monkeypatching: accurev.client.Client.cmd with our own implementation'
accurev.client.Client.cmd = cmd
