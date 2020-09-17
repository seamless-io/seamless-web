from core.models import get_db_session, User
from core.models.workspaces import Plan
from core.services.user import sign_up


def test_personal(postgres):
    """
    When user is registered with using "Personal" plan or default "Sign Up" next things should happen:
    * User record should be created
    * Personal Workspace should be created
    * Registered user should be a part of workspace created
    """
    plan = Plan.Personal.value
    email = f"sign_up_{plan}_test@test.com"
    sign_up(email, plan)

    user = User.get_user_from_email(email, get_db_session())
    assert len(list(user.owned_workspaces)) == 1
    workspace = user.owned_workspaces[0]
    assert workspace.plan == plan
    assert workspace.subscription_is_active is True


def test_startup():
    """
    When user is registered with "Startup":
    * Extra fields while registration pop-up: "Team Name"
    * Personal Workspace created
    * {Team name} workspace created
    * Registered user becomes part of Personal Workspace and {Team name} workspace
    * User become and owner (the one who is paying for a team)
    * Private Job Templates initialized (still TODO)
    """
    pass


def test_business():
    """
    When user is registered with "Business":
    * Extra fields while registration pop-up: "Team Name"
    * Personal Workspace created
    * {Team name} workspace created
    * Registered user becomes part of Personal Workspace and {Team name} workspace
    * User become and owner (the one who is paying for a team)
    * Private Job Templates initialized (still TODO)
    * 4 office hours with us
    """
    pass


def test_enterprise():
    """
    When user is registered with "Enterprize":
    * Extra fields while registration pop-up: "Team Name"
    * Personal Workspace created
    * {Team name} workspace created
    * Registered user becomes part of Personal Workspace and {Team name} workspace
    * User become and owner (the one who is paying for a team)
    * Private Job Templates initialized (still TODO)
    * 4 office hours with us
    """
    pass
