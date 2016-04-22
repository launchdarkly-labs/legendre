import boto3
import os
from botocore.exceptions import ClientError

iam = boto3.resource('iam')
lambda_client = boto3.client('lambda')
events_client = boto3.client('events')
iam_client = boto3.client('iam')

base_dir = os.path.dirname(os.path.realpath(__file__))

def iam_role():
  try:
    iam_client.get_role(RoleName='legendre')
  except ClientError as e:
    if e.response['Error']['Code'] == 'NoSuchEntity':
      with open('{}/lambda_role_policy.json'.format(base_dir), 'r') as policy_file:
        policy = policy_file.read()
        iam_client.create_role(
          RoleName='legendre',
          AssumeRolePolicyDocument=policy)
    else:
      raise e

  for rp in ['ec2_access', 'sns_access', 'cloudwatch_logs_access']:
    with open('{}/{}.json'.format(base_dir, rp), 'r') as policy_file:
      policy = policy_file.read()
      iam_client.put_role_policy(
        RoleName='legendre',
        PolicyName=rp,
        PolicyDocument=policy)
  try:
    iam_client.get_instance_profile(InstanceProfileName='legendre')
  except ClientError as e:
    if e.response['Error']['Code'] == 'NoSuchEntity':
      iam_client.create_instance_profile(InstanceProfileName='legendre')
    else:
      raise e

  role_instance_profiles = iam_client.list_instance_profiles_for_role(RoleName='legendre')
  should_add_instance_profile_to_role = True
  for p in role_instance_profiles['InstanceProfiles']:
    if p['InstanceProfileName'] == 'legendre':
      should_add_instance_profile_to_role = False
  if should_add_instance_profile_to_role:
    iam_client.add_role_to_instance_profile(InstanceProfileName='legendre', RoleName='legendre')
  return iam.Role('legendre')

def get_vpc_config():
  vpc_config = {}
  subnet_id = os.environ.get('SUBNET_ID')
  secuity_group_id = os.environ.get('SECURITY_GROUP_ID')
  if subnet_id:
    vpc_config['SubnetIds'] = [ subnet_id ]
  if secuity_group_id:
    vpc_config['SecurityGroupIds'] = [ secuity_group_id ]
  return vpc_config

def upload_function():
  vpc_config = get_vpc_config()
  role = iam_role()

  # You can't actually set up a schedule for lamda functions via the API :(
  # http://docs.aws.amazon.com/lambda/latest/dg/intro-core-components.html#intro-core-components-event-sources
  # grep for 'there is no AWS Lambda API to configure this mapping'
  # rule = events_client.put_rule(
  #   Name='FindZombieInstancesSchedule',
  #   ScheduleExpression='rate(5 minutes)',
  #   State='ENABLED',
  #   Description='Run the zombie instance detector on a schedule',
  #   RoleArn=role.arn,
  # )

  with open('{}/../legendre.zip'.format(base_dir), 'rb') as zip_file:
    zip_bytes = zip_file.read()
    func = {}
    try:
      lambda_client.get_function(FunctionName='FindZombieInstances')
      func = lambda_client.update_function_code(
        FunctionName='FindZombieInstances',
        ZipFile=zip_bytes,
        Publish=True,
      )
    except ClientError as e:
      if e.response['Error']['Code'] == 'ResourceNotFoundException':
        func = lambda_client.create_function(
          FunctionName='FindZombieInstances',
          Code= {
            'ZipFile': zip_bytes,
          },
          Runtime='python2.7',
          Role=role.arn,
          Handler='legendre.handler',
          Timeout=30,
          Description="Detect zombie EC2 instances and notify",
          MemorySize=128,
          VpcConfig=vpc_config
        )
      else:
        raise e

    # events_client.put_targets(
    #   Rule='FindZombieInstancesSchedule',
    #   Targets=[
    #     { 'Id': 'FindZombieInstances-schedule',
    #       'Arn': '{}:$LATEST'.format(func['FunctionArn']),
    #     }
    #   ]
    # )

upload_function()