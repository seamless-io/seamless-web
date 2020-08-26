import cron_descriptor
import pytest

from core.helpers import parse_cron


def test_parse_cron():
    assert ('15 10 * * ? *',
            'At 10:15 AM') == parse_cron('15 10 * * *')
    assert ('0 18 ? * MON-FRI *',
            'At 06:00 PM, Monday through Friday') == parse_cron('0 18 * * MON-FRI')
    assert ('0 8 1 * ? *',
            'At 08:00 AM, on day 1 of the month') == parse_cron('0 8 1 * *')
    assert ('0/10 * ? * MON-FRI *',
            'Every 10 minutes, Monday through Friday') == parse_cron('0/10 * * * MON-FRI')
    assert ('0/5 8-17 ? * MON-FRI *',
            'Every 5 minutes, between 08:00 AM and 05:59 PM, Monday through Friday') == parse_cron(
        '0/5 8-17 * * MON-FRI')

    with pytest.raises(cron_descriptor.Exception.FormatException):
        parse_cron('10 * * *')
        parse_cron('THIS IS WRONG')
        parse_cron('* * * * no')
