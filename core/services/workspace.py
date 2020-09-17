from core.models import Workspace, get_db_session, db_commit
from core.models.workspaces import Plan


def create_workspace(user_id: str, plan: Plan):
    """
    Creates a workspace record in the database and assigns user as an owner
    """
    workspace = Workspace(owner_id=user_id,
                          name=plan.value,  # TODO later we will let the user choose the name
                          plan=plan.value,
                          # subscription should be activated after the first payment
                          subscription_is_active=True if plan == plan.Personal else False)
    db_session = get_db_session()
    db_session.add(workspace)
    db_commit()
    return workspace.id
