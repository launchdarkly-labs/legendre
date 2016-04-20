import requests

notify_sns_topic_name = 'legendre'

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

# Modify this function to get the live version from your running apps
def get_expected_sha(tier, app_name):
  status_resource = app_status_resources[tier][app_name]
  r = requests.get(status_resource)
  resp = r.json()
  return resp['version']