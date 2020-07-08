import os

import requests


def lambda_handler(event, context):
    url = f"https://schedule_events_proxy:{os.getenv('SNS_PASSWORD')}@app.seamlesscloud.io/schedule/jobs/execute"
    requests.post(url, json=event)
