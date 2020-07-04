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


# def generate_logs(api_key: str, logstream: Iterable[bytes], timestamp_str: str):
#     cloud_watch = boto3.client('logs', region_name=os.getenv('AWS_REGION_NAME'))
#     log_group_name = f'/seamless/api_key/{api_key}'
#     try:
#         cloud_watch.create_log_group(
#             logGroupName=log_group_name
#         )
#         cloud_watch.put_retention_policy(
#             logGroupName=log_group_name,
#             retentionInDays=JOB_LOGS_RETENTION_DAYS
#         )
#     except ClientError as e:
#         if e.response['Error']['Code'] == 'ResourceAlreadyExistsException':
#             pass  # If log group already exists - it's fine
#         else:
#             raise e
#     cloud_watch.create_log_stream(
#         logGroupName=log_group_name,
#         logStreamName=timestamp_str
#     )

#     sequence_token = None
#     for line in logstream:
#         log_args = {
#             'logGroupName': log_group_name,
#             'logStreamName': timestamp_str,
#             'logEvents': [
#                 {
#                     'timestamp': int(round(time.time() * 1000)),
#                     'message': str(line, "utf-8")
#                 }
#             ],

#         }
#         if sequence_token:
#             log_args.update({
#                 'sequenceToken'
#                 : sequence_token
#             })
#         response = cloud_watch.put_log_events(**log_args)
#         sequence_token = response['nextSequenceToken']
#         yield line
