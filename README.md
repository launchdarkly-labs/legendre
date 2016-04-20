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
There are a few things you need to do to set this up for yourself. Copy the `custom_exaple.py` to `custom.py`, and fill it in for your environment.  

* Set `notify_sns_topic_name` to the SNS topic that you want to use.  It's okay if it doesn't exist yet; the script can create it, but you will still need to set the subscriptions to do something useful.
* Set up the `app_status_resources` dict to define the applications and tiers in your system.  The URLs are meant to be status check resources (via a load balancer) that can be used to get the running version.
* Define `get_expected_sha` to determine what is the 'current' version of the given application in a given tier.  Any different version will be deemed a zombie.

Create IAM role
---
Next, you will need to create an IAM role to give the lambda task access to get information about your running instances, and to send SNS notifications.  You can do this by simply running the shell script:

    $ iam/create_iam_role.sh
    
Of course, you can inspect the permissions being granted to the task by looking in the JSON files in the `iam` directory.