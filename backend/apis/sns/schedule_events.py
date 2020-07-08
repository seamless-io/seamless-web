import logging

import requests
from flask import Blueprint, request
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import check_password_hash, generate_password_hash

from backend.config import SNS_PASSWORD

schedule_events_bp = Blueprint('schedule_events', __name__)

auth = HTTPBasicAuth()


@auth.verify_password
def verify_password(username, password):
    logging.info(username)
    logging.info(password)
    if username == 'sns' and\
            check_password_hash(generate_password_hash(SNS_PASSWORD), password):
        return username


# events from SNS sent to this endpoint (see beanstalk config)
@schedule_events_bp.route('/jobs/execute', methods=['POST'])
@auth.login_required
def run_job_by_schedule():
    message = request.get_json(force=True)
    logging.info(message)
    logging.info(auth.current_user())
    if message['Type'] == 'SubscriptionConfirmation':
        confirmation_url = message['SubscribeURL']
        res = requests.get(confirmation_url)
        res.raise_for_status()
        return "Success", 200
    else:
        pass
    return "Success", 200
    # job_id = request.json['job_id']
    # with session_scope() as db_session:
    #     job = db_session.query(Job).get(job_id)
    #     if not job:
    #         return "Job Not Found", 404
    #
    #     job.status = JobStatus.Executing.value
    #     job_run = JobRun(job_id=job_id,
    #                      type=JobRunType.Schedule.value)
    #     db_session.add(job_run)
    #     db_session.commit()
    #
    #     emit('status', {'job_id': job_id,
    #                     'job_run_id': job_run.id,
    #                     'status': job.status},
    #          namespace='/socket',
    #          broadcast=True)
    #     path_to_job_files = get_path_to_job(JobType.PUBLISHED, job.user.api_key, str(job.id))
    #     executor.execute_and_stream_to_db(path_to_job_files, str(job.id), str(job_run.id))
    #     return f"Running job {job.name}", 200
