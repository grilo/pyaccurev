# pyaccurev
Python wrapper for the AccuRev CLI (tested against 5.6)

# Usage
```python
import accurev.client
client = accurev.client.Client()

print 'Stream count:', len(client.depots['OFFICE'].streams)

for stream in client.depots['OFFICE'].streams:
    print stream

print client.depots['OFFICE'].streams['feature_branch_2.0']


print depot.streams['feature_branch_2.0'].workspaces
print depot.streams['feature_branch_2.0'].issues

print depot.streams['feature_branch_2.0'].issues.values()[0].developers

for e in client.depots['OFFICE'].streams['feature_branch_2.0'].issues['JIRA-37'].elements.values():
    if e.missing == "false":
        print e

 Promote by issue
for issue in client.depots['OFFICE'].streams['feature_branch_2.0'].issues.values():
    if issue.IDJira == 'JIRA-37':
        out, err = client.promote_issues([issue.issueNum], issue.stream.name, 'feature_branch_sandbox')
        print out

for dep in client.depots['OFFICE'].streams['feature_branch_2.0'].issues['JIRA-37'].dependencies.values():
    print dep
```
