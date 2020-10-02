from core.models import Workspace, get_db_session, db_commit
from core.models.plans import WorkspacePlanSize, WorkspacePlan
from core.models.subscriptions import SubscriptionName, Subscription

SUBSCRIPTION_TO_WORKSPACE_PLAN_MAP = {
    SubscriptionName.Personal: WorkspacePlanSize.S,
    SubscriptionName.Startup: WorkspacePlanSize.M,
    SubscriptionName.Business: WorkspacePlanSize.L,
}


def create_workspace_plan(subscription: Subscription, workspace: Workspace):
    plan = WorkspacePlan(subscription_id=subscription.id,
                         workspace_id=workspace.id,
                         size=SUBSCRIPTION_TO_WORKSPACE_PLAN_MAP[subscription.name].value)
    get_db_session().add(plan)
    db_commit()
