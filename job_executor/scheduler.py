import json
import logging
import os

import boto3
from botocore.exceptions import ClientError


def _generate_cloudwatch_rule_name(job_id: str, stage: str) -> str:
    return f"{stage}-job-{job_id}"


def schedule(cron_schedule: str, job_id: str, is_active: bool) -> str:
    """
    TODO: do not use project_path as an identifier for events
    """
    cloudwatch_rule_name = _generate_cloudwatch_rule_name(job_id, os.getenv('STAGE', 'local'))
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
                'Id': os.getenv('LAMBDA_PROXY_NAME'),
                'Arn': os.getenv('LAMBDA_PROXY_ARN'),
                'Input': json.dumps({'job_id': job_id}),
            }
        ]
    )
    logging.info(f"Configured target for CW rule: {res}")
    return rule_arn  # TODO: store it somewhere


def enable_job_schedule(job_id: str):
    events = boto3.client('events', region_name=os.getenv('AWS_REGION_NAME'))
    rule_name = _generate_cloudwatch_rule_name(job_id, os.getenv('STAGE', 'local'))
    events.enable_rule(Name=rule_name)
    logging.info(f"Schedule rule {rule_name} enabled")


def disable_job_schedule(job_id: str):
    events = boto3.client('events', region_name=os.getenv('AWS_REGION_NAME'))
    rule_name = _generate_cloudwatch_rule_name(job_id, os.getenv('STAGE', 'local'))
    events.disable_rule(Name=rule_name)
    logging.info(f"Schedule rule {rule_name} disabled")


def remove_job_schedule(job_id: str):
    events = boto3.client('events', region_name=os.getenv('AWS_REGION_NAME'))
    cloudwatch_rule_name = _generate_cloudwatch_rule_name(job_id, os.getenv('STAGE', 'local'))
    try:
        events.remove_targets(Rule=cloudwatch_rule_name,
                              Ids=[os.getenv('LAMBDA_PROXY_NAME')])
        events.delete_rule(Name=cloudwatch_rule_name)
        logging.info(f"Schedule of job {job_id} removed from CloudWatch rules")
    except ClientError as e:
        error_code = e.response.get("Error", {}).get("Code")
        if error_code == "ResourceNotFoundException":
            logging.info(f"Schedule of job {job_id} was not removed from CloudWatch rules because it's not there")
        else:
            raise e
