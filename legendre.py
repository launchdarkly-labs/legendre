import boto3
import requests
import json
from itertools import chain
from custom import get_expected_sha, app_status_resources, notify_sns_topic_name
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

client = boto3.client('ec2')
sns_client = boto3.client('sns')

def find_instances():
  response = client.describe_instances(
    DryRun=False,
    Filters=[],
  )
  for r in response['Reservations']:
    for i in r['Instances']:
      yield i

def find_unnamed_instances():
  logger.info('looking for unnamed instances')
  for i in find_instances():
    has_name = False
    for t in i.get('Tags', []):
      if t['Key'] == 'Name' and len(t['Value']) > 0 :
        has_name = True
    if not has_name:
      yield i

def find_stale_app_instances(tier, app_name):
  logger.info('looking for stale app instances')
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
  for tier, apps in app_status_resources.iteritems():
    for app in apps:
      yield find_stale_app_instances(tier, app)

def notify_zombie(instance):
  arn = sns_client.create_topic(Name=notify_sns_topic_name)['TopicArn']
  tags = instance.get('Tags', {})
  sns_client.publish(TopicArn=arn, Message="Found zombie instance {}. Tags: {}".format(instance['InstanceId'], json.dumps(tags)))

def handler(event, context):
  for i in chain.from_iterable(problematic_instances()):
    logger.warn('found zombie instance: {}'.format(i))
    notify_zombie(i)
