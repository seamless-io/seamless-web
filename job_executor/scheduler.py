import os
import json
import logging

import boto3

import config


def schedule(cron_schedule: str, job_id: str, is_active: bool) -> str:
    """
    TODO: do not use project_path as an identifier for events
    """
    events = boto3.client('events', region_name=os.getenv('AWS_REGION_NAME'))
    logging.info(f"Scheduling job (id:{job_id}): {cron_schedule} (active: {is_active})")
    result = events.put_rule(
        Name=f"{config.STAGE}/job/{job_id}",
        ScheduleExpression=f"cron({cron_schedule})",  # TODO: convert default cron to AWS cron
        State='ENABLED' if is_active else 'DISABLED'
    )
    rule_arn = result['RuleArn']
    logging.info(f"Cloudwatch Event Rule was configured succesfully. Rule ARN: {rule_arn}")

    res = events.put_targets(
        Rule=job_id,
        Targets=[
            {
                'Id': config.LAMBDA_PROXY_NAME,
                'Arn': config.LAMBDA_PROXY_ARN,
                'Input': json.dumps({'job_id': job_id}),
            }
        ]
    )
    logging.info(f"Configured target for CW rule: {res}")
    return rule_arn  # TODO: store it somewhere


def enable_job_schedule(job_id: str):
    events = boto3.client('events', region_name=os.getenv('AWS_REGION_NAME'))
    events.enable_rule(Name=job_id)


def disable_job_schedule(job_id: str):
    events = boto3.client('events', region_name=os.getenv('AWS_REGION_NAME'))
    events.disable_rule(Name=job_id)
