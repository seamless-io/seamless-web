"""
Module defining working with JobPlans
"""
from core.models import get_db_session, db_commit
from core.models.jobs import Job
from core.models.plans import JobPlan, JobCharge

from core.services.subscription import NoSubscriptionError


def create_plan(job: 'Job'):
    """
    If this is the first job in personal workspace - creates a free plan
    """
    session = get_db_session()
    if job.workspace.personal is True:
        existing_jobs_count = session.query(Job).filter_by(workspace_id=job.workspace.id,
                                                           user_id=job.workspace.owner_id).count()
        if existing_jobs_count == 1:
            return

    if not job.workspace.owner.subscription_id:
        raise NoSubscriptionError

    job_plan = JobPlan(
        job_id=job.id,
        subscription_id=job.workspace.owner.subscription_id
    )
    session.add(job_plan)
    db_commit()




def calculate_charge(plan_id: int):
    """
    Function for calculating charge for the job/day.
    Should be triggered on:
    * Job deletion
    * Somebody is looking at how much money he needs to pay
    * End of the subscription period
    """
    pass
