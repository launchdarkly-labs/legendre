import boto3
import requests
from itertools import chain

app_status_resources = {
  'production': {
    'frontend': 'http://lb-internal.prod.example.com:3000/api/status',
    'backend-thing': 'http://lb-internal.prod.example.com:4040/private/status',
    'other-backend-thing': 'http://lb-internal.prod.example.com:3030/private/status',
  },
  'staging': {
    'frontend': 'http://lb-internal.stg.example.com:3000/api/status',
    'backend-thing': 'http://lb-internal.stg.example.com:4040/private/status',
    'other-backend-thing': 'http://lb-internal.stg.example.com:3030/private/status',
  },
  'dogfood': {
    'frontend': 'http://lb-internal.dog.example.com:3000/api/status',
    'backend-thing': 'http://lb-internal.dog.example.com:4040/private/status',
    'other-backend-thing': 'http://lb-internal.dog.example.com:3030/private/status',
  },
}

client = boto3.client('ec2')

# Modify this function to get the live version from your running apps
def get_expected_sha(tier, app_name):
  status_resource = app_status_resources[tier][app_name]
  r = requests.get(status_resource)
  resp = r.json()
  return resp['version']

def find_instances():
  response = client.describe_instances(
    DryRun=False,
    Filters=[],
  )
  for r in response['Reservations']:
    for i in r['Instances']:
      yield i

def find_unnamed_instances():
  for i in find_instances():
    has_name = False
    for t in i.get('Tags', []):
      if t['Key'] == 'Name' and len(t['Value']) > 0 :
        has_name = True
    if not has_name:
      yield i

def find_stale_app_instances(tier, app_name):
  expected_sha = get_expected_sha(tier, app_name)
  response = client.describe_instances(
    DryRun=False,
    Filters=[
      {
        'Name': 'tag:tier',
        'Values': [
          tier,
        ]
      },
      {
        'Name': 'tag:app',
        'Values': [
          app_name,
        ]
      },
    ],
  )
  for r in response['Reservations']:
    for i in r['Instances']:
      is_expected_sha = False
      for t in i['Tags']:
        if t['Key'] == 'sha' and t['Value'] == expected_sha:
          is_expected_sha = True
      if not is_expected_sha:
        yield i

def problematic_instances():
  yield find_unnamed_instances()
  for tier in ['production', 'staging', 'dogfood']:
    for app in ['gonfalon', 'event-recorder', 'attribute-recorder']:
      yield find_stale_app_instances(tier, app)

for i in chain.from_iterable(problematic_instances()):
  print i['InstanceId'], i.get('Tags')
  