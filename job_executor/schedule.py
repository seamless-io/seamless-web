import os
import json

import boto3


def schedule(cron_schedule: str, project_path: str) -> str:
    """
    TODO: do not use project_path as an identifier for events
    """
    events = boto3.client('events', region_name=os.getenv('AWS_REGION_NAME'))

    result = events.put_rule(
        Name=project_path,
        ScheduleExpression=f"cron({cron_schedule})",  # TODO: convert default cron to AWS cron
        State='ENABLED'
    )
    print(f'\n\nRule Results:\n {result}')
    rule_arn = result['RuleArn']

    # TODO: create SQS in terraform
    res = events.put_targets(
        Rule=project_path,
        Targets=[
            {
                'Id': 'scheduled-to-execute.fifo',
                'Arn': 'arn:aws:sqs:us-east-1:202868668807:scheduled-to-execute.fifo',
                'Input': json.dumps({'project_path': project_path}),
                'SqsParameters': {
                    'MessageGroupId': 'project'  # TODO: figure our why do we need message group
                }

            }
        ]
    )
    print(f"\n\nPut Targets result:\n {res}")
    return rule_arn  # TODO: store it somewhere
