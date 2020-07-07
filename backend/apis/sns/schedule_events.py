import logging
import pprint

from flask import Blueprint, request

schedule_events_bp = Blueprint('schedule_events', __name__)


# TODO: figure out auth
@schedule_events_bp.route('/jobs/execute', methods=['POST'])  # events from SQS sent to this endpoint (see beanstalk config)
def run_job_by_schedule():
    logging.info(request.json)
    logging.info(request.args)
    logging.info(request.headers)
    logging.info(request.get_data())
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
