from core.models import Workspace, get_db_session, db_commit, User
from core.models.users_workspaces import UserWorkspace
from core.models.workspaces import Plan


class WorkspaceNotFound(Exception):
    pass


class PlanChangeError(Exception):
    pass


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


def get_user_personal_workspace(user_id: str):
    """
    Every user has a Personal workspace - this is the logic to get it
    """
    user = get_db_session().query(User).filter(User.id == user_id).one()
    return user.owned_workspaces.filter(Workspace.plan == Plan.Personal.value).one()


def add_user_to_workspace(user_id: str, workspace_id: str):
    """
    Adds the user to the workspace so the user can access jobs inside that workspace
    """
    user_workspace_link = UserWorkspace(user_id=user_id, workspace_id=workspace_id)
    get_db_session().add(user_workspace_link)
    db_commit()
    return user_workspace_link.id


def get_available_workspaces(user_id: str):
    user_workspace_links = get_db_session().query(UserWorkspace).filter(
        UserWorkspace.user_id == user_id).all()
    workspaces_ids = [link.workspace_id for link in user_workspace_links]
    return get_db_session().query(Workspace).filter(Workspace.id.in_(workspaces_ids)).all()


def upgrade_workspace(user_id: str, workspace_id: str, plan: str):
    user = get_db_session().query(User).filter(User.id == user_id).one()
    workspace = user.owned_workspaces.filter(Workspace.id == workspace_id).one_or_none()
    if not workspace:
        raise WorkspaceNotFound("Workspace does not exists or the user does not own it.")

    if plan == Plan.Business.value and workspace.plan == Plan.Startup.value:
        # That's the only supported upgrade for now
        workspace.plan = plan
        workspace.subscription_is_active = False  # The user needs to pay for the new plan first
        # Note that if we do not implement a feature for user to pick the name of the workspace,
        # We can end up with workspace named Startup and on Business plan, which could be a bit confusing
        db_commit()
    else:
        raise PlanChangeError(f"Cannot upgrade {workspace.plan} to {plan}")


def downgrade_workspace(user_id: str, workspace_id: str, plan: str):
    user = get_db_session().query(User).filter(User.id == user_id).one()
    workspace = user.owned_workspaces.filter(Workspace.id == workspace_id).one_or_none()
    if not workspace:
        raise WorkspaceNotFound("Workspace does not exists or the user does not own it.")

    if plan == Plan.Startup.value and workspace.plan == Plan.Business.value:
        # That's the only supported downgrade for now
        workspace.plan = plan
        # TODO we need to do something about the money user already spent on paying for the more expensive plan
        # Note that if we do not implement a feature for user to pick the name of the workspace,
        # We can end up with workspace named Business and on Startup plan, which could be a bit confusing
        db_commit()
    else:
        raise PlanChangeError(f"Cannot downgrade {workspace.plan} to {plan}")


def invite_user(user_id: str, workspace_id: str):
    """
    When a user adding another one to his workspace
    """
    pass


def remove_user(user_id: str, workspace_id: str):
    """
    Removes user from the workspace:
    * by owner
    * by the user itself
    """
    pass


def accept_invintation(user_id: str, workspace_id: str):
    """
    When user follows a link in the email with invintation to workspace
    """
    pass
