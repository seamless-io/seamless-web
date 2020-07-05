import os
import json

import boto3


QUEUE_ID = 'scheduled-to-execute.fifo'
QUEUE_ARN = 'arn:aws:sqs:us-east-1:202868668807:scheduled-to-execute.fifo'


def schedule(cron_schedule: str, job_id: str) -> str:
    """
    TODO: do not use project_path as an identifier for events
    """
    events = boto3.client('events', region_name=os.getenv('AWS_REGION_NAME'))

    result = events.put_rule(
        Name=job_id,
        ScheduleExpression=f"cron({cron_schedule})",  # TODO: convert default cron to AWS cron
        State='ENABLED'
    )
    rule_arn = result['RuleArn']

    # TODO: create SQS in terraform
    events.put_targets(
        Rule=job_id,
        Targets=[
            {
                'Id': QUEUE_ID,
                'Arn': QUEUE_ARN,
                'Input': json.dumps({'job_id': job_id}),
                'SqsParameters': {
                    'MessageGroupId': 'project'  # TODO: figure our why do we need message group
                }

            }
        ]
    )
    return rule_arn  # TODO: store it somewhere
