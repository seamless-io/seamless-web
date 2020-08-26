from datetime import datetime
from typing import Tuple

from cron_descriptor import FormatException

from cron_descriptor import get_description

# https://stackoverflow.com/questions/1958219/convert-sqlalchemy-row-object-to-python-dict
from croniter import croniter


class InvalidCronException(Exception):
    pass


def row2dict(row):
    d = {}
    for column in row.__table__.columns:
        d[column.name] = str(getattr(row, column.name))

    return d


def parse_cron(expression: str) -> Tuple[str, str]:
    if '?' in expression:
        raise InvalidCronException(f"Cannot parse the cron expression: '?' symbols are not allowed\n"
                                   f"Please use https://crontab.guru/#{expression.replace(' ', '_')} as a reference.")
    try:
        human_readable_description = get_description(expression)
        aws_cron = _cron_to_aws_cron(expression)
    except FormatException as e:
        raise InvalidCronException(f"Cannot parse the cron expression: {str(e)}\n You can find out what part of your "
                                   "expression is not written in a standard notation by following this link "
                                   f"https://crontab.guru/#{expression.replace(' ', '_')}.")
    except ValueError as e:
        if 'too many values to unpack (expected 5)' in str(e):
            raise InvalidCronException("Currently we support only cron expressions that consist of 5 parts. "
                                       "Your expression had more. "
                                       "If you have any questions please shoot an email at hello@seamlesscloud.io")
        else:
            raise e
    return aws_cron, human_readable_description


def _cron_to_aws_cron(expression: str) -> str:
    """
    :param expression: Cron expression in the standard format (https://crontab.guru/)
    :return: AWS-compatible cron expression
    Please note that not all features available in AWS cron could be used if we convert from the standard cron.
    In particular, standard cron does not support setting year and expressions like "first Monday of a month".
    More info on AWS cron expressions here
    https://docs.aws.amazon.com/AmazonCloudWatch/latest/events/ScheduledEvents.html.
    """
    minute, hour, day_of_month, month, day_of_week = expression.split()
    year = "*"
    if day_of_month == "*":
        if day_of_week == "*":
            day_of_week = "?"
        else:
            day_of_month = "?"
    else:
        if day_of_week == "*":
            day_of_week = "?"
        else:
            raise CronConversionException(
                "You cannot specify both day_of_month and day_of_week in a single cron expression. "
                "This is a limitation aimed to make your jobs less error-prone.")
            # To be honest this is an AWS limitation
    return " ".join([minute, hour, day_of_month, month, day_of_week, year])


class CronConversionException(Exception):
    pass


def get_cron_next_execution(expression: str) -> str:
    cron = croniter(expression, datetime.utcnow())
    return cron.get_next(datetime).strftime('%B %d, %Y, %H:%M:%S')
