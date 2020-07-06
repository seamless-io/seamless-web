import os
import json
import logging

import boto3


QUEUE_ID = 'jobs.fifo'
QUEUE_ARN = 'arn:aws:sqs:us-east-1:202868668807:jobs.fifo'


def schedule(cron_schedule: str, job_id: str, is_active: bool) -> str:
    """
    TODO: do not use project_path as an identifier for events
    """
    logging.info(f"Scheduling job (id:{job_id}): {cron_schedule} (active: {is_active})")
    events = boto3.client('events', region_name=os.getenv('AWS_REGION_NAME'))

    result = events.put_rule(
        Name=job_id,
        ScheduleExpression=f"cron({cron_schedule})",  # TODO: convert default cron to AWS cron
        State='ENABLED' if is_active else 'DISABLED'
    )
    rule_arn = result['RuleArn']
    logging.info(f"Cloudwatch Event Rule was configured succesfully. Rule ARN: {rule_arn}")

    # TODO: create SQS in terraform
    res = events.put_targets(
        Rule=job_id,
        Targets=[
            {
                'Id': QUEUE_ID,
                'Arn': QUEUE_ARN,
                'Input': json.dumps({'job_id': job_id}),  # TODO: send auth codes to recognize them in client/jobs.py
                'SqsParameters': {
                    'MessageGroupId': 'project'  # TODO: figure our why do we need message group
                }
            }
        ]
    )
    logging.info(f"Configured target for CW rule: {res}")
    return rule_arn  # TODO: store it somewhere
