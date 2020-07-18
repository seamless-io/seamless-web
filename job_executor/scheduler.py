import os
import json
import logging

import boto3

import config


def _generate_cloudwatch_rule_name(job_id: str, stage: str) -> str:
    return f"{stage}-job-{job_id}"


def schedule(cron_schedule: str, job_id: str, is_active: bool) -> str:
    """
    TODO: do not use project_path as an identifier for events
    """
    cloudwatch_rule_name = _generate_cloudwatch_rule_name(job_id, config.STAGE)
    events = boto3.client('events', region_name=os.getenv('AWS_REGION_NAME'))
    logging.info(f"Scheduling job (id:{job_id}): {cron_schedule} (active: {is_active})")
    result = events.put_rule(
        Name=cloudwatch_rule_name,
        ScheduleExpression=f"cron({cron_schedule})",  # TODO: convert default cron to AWS cron
        State='ENABLED' if is_active else 'DISABLED'
    )
    rule_arn = result['RuleArn']
    logging.info(f"Cloudwatch Event Rule was configured succesfully. Rule ARN: {rule_arn}")

    res = events.put_targets(
        Rule=cloudwatch_rule_name,
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


def remove_job_schedule(job_id: str):
    events = boto3.client('events', region_name=os.getenv('AWS_REGION_NAME'))
    cloudwatch_rule_name = _generate_cloudwatch_rule_name(job_id, config.STAGE)
    events.remove_targets(Rule=cloudwatch_rule_name,
                          Ids=[config.LAMBDA_PROXY_NAME])
    events.delete_rule(Name=cloudwatch_rule_name)
