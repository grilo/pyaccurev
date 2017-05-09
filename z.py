#import xml.etree.cElementTree as et
#
#
#out = open('a.xml', 'r').read()
#
#for issue in et.fromstring(out).findall('./issues/issue'):
#    for child in issue:
#        print child.tag
#        print child.text
#
#

import accurev.issue

props = {'status': 'InProgress', 'IDNotes': 'STRY0024187', 'stream': 'FRONT_APPS_INT', 'shortDescription': 'STRY0024187 Navigation options from product page', 'issueNum': '57426', 'assignedTo': 'Administrator', 'state': 'Pending', 'dateSubmitted': '1485185468', 'developers': 'LK46MB\nHL87VP', 'type': 'FUNC - Funcionalidad', 'transNum': '4082731'}

i = accurev.issue.Issue('dummy', **props)
print i
