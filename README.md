Get control of your zombie instances
====

Sometimes things go wrong and deploy scripts get interrupted before they finish cleaning up old instances.  These
zombie instances lurk around, eating the brains^H^H^H^H^H^Hhard-earned money you pay to AWS each month.

<iframe class="imgur-embed" width="100%" height="undefined" frameborder="0" src="http://i.imgur.com/9ZzuLyN.gifv#embed"></iframe>

This tool is intended to be run routinely from AWS lambda, and it will detect zombie instances, notifying you about them via SNS.

Assumptions
---
This assumes that you use EC2 tags in a certain way, that you use a load balancer, and that your applications have a status resource that returns their current version.

The tags you need are:

| Tag name | Purpose | Example |
|---|---|---|
| tier | separate environments | production, staging, etc|
| app | identify services | frontend-app, backend-thing, other-backend-thing|
| sha | version or build number | 123abc |

Getting started
---
There are a few things you need to do to set this up for yourself. Copy the `custom_exaple.py` to `custom.py`, and fill it in 
for your environment.  

* Set `notify_sns_topic_name` to the SNS topic that you want to use.  It's okay if it doesn't exist yet; the script can create 
it, but you will still need to set the subscriptions to do something useful.
* Set up the `app_status_resources` dict to define the applications and tiers in your system.  The URLs are meant to be status 
check resources (via a load balancer) that can be used to get the running version.
* Define `get_expected_sha` to determine what is the 'current' version of the given application in a given tier.  Any different 
version will be deemed a zombie.

Also, the deploy needs a few environment variables set.  Edit `vars.sh` to set the subnet and security group for the lambda 
function to run inside your VPC.

Run the deploy script
---
When you are ready to deploy, run `./deploy_lambda_function.sh`.  This will:

* Package up the script with its dependencies into the zip format that AWS Lambda expects (as defined in `pacakge.sh`).
* Interact with the AWS API to set up the lambda function with *most* of the things it needs (as defined in `scripts/setup_lambda.py`):
  * Creates an IAM role for the lambda function to use.  Review the json files in the `scripts` folder to see the permisisons 
  required.
  * Uploads the zip file from the previous step to create a Lambda function (possibly publishing a new version if the function 
  already exists).

However, there are a couple of things you still need to do:

* Add subscribers to the SNS topic. This will be highly personalized to your needs.  Maybe you want an email sent. Maybe you want 
a webhook to notify your team in HipChat. Maybe you want it to trigger another lambda function that will kill the zombie 
instances. Maybe you want it to sound an air-raid siren. I'll leave this as an exercise to the reader.
* [Set up the schedule](http://docs.aws.amazon.com/lambda/latest/dg/tutorial-scheduled-events-create-function.html). It seems 
that there is no way to set up a Cloudwatch Events schedule to trigger Lambda functions via the API; it needs to be done in the 
web console.  (You can create Cloudwatch Events schedule rules in the API, but it seems they cannot trigger Lambda functions.  
The [Lambda Docs](http://docs.aws.amazon.com/lambda/latest/dg/intro-core-components.html#intro-core-components-event-sources) 
mentions "there is no AWS Lambda API to configure this mapping").