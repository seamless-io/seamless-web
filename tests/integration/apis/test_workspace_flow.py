from flask.testing import FlaskClient

from application import application
from core.models import get_db_session, User
from core.models.users_workspaces import UserWorkspace
from core.models.workspaces import Plan
from core.services.user import sign_up


def _get_web_client_with_credentials(user_id, user_email):
    """
    Web client fixture. This fixture should be used when we are testing api's used by the frontend and complying
    with auth0 authentication
    """
    application.config['TESTING'] = True
    # This is a default class, but we need to explicitly set it because cli_client overwrites it
    application.test_client_class = FlaskClient

    with application.test_client() as client:
        with client.session_transaction() as session:
            session['jwt_payload'] = session['profile'] = {
                'auth0_user_id': user_id,  # no matter what is in here
                'email': user_email,
                'user_id': user_id
            }
        return client


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

    # Let's also check that the user is added to the Workspace
    get_db_session().query(UserWorkspace).filter(
        UserWorkspace.user_id == user.id, UserWorkspace.workspace_id == workspace.id).one()

    client = _get_web_client_with_credentials(user.id, email)

    resp = client.get('/api/v1/workspaces')
    assert resp.status_code == 200
    assert len(resp.json) == 1

    assert resp.json[0]['owner_id'] == str(user.id)
    assert resp.json[0]['plan'] == plan
    assert resp.json[0]['subscription_is_active'] == 'True'

    # We should not be able to upgrade or downgrade Personal workspace
    resp = client.post(f'/api/v1/workspaces/{str(workspace.id)}/upgrade/Startup')
    assert resp.status_code == 400
    resp = client.post(f'/api/v1/workspaces/{str(workspace.id)}/upgrade/Business')
    assert resp.status_code == 400
    resp = client.post(f'/api/v1/workspaces/{str(workspace.id)}/downgrade/Startup')
    assert resp.status_code == 400
    resp = client.post(f'/api/v1/workspaces/{str(workspace.id)}/downgrade/Business')
    assert resp.status_code == 400


def test_startup(postgres):
    """
    When user is registered with "Startup":
    * Personal Workspace created
    * Startup workspace created (TODO make workspace name configurable)
    * Registered user becomes an owner of Personal Workspace and Startup workspace
    * Private Job Templates initialized (still TODO)
    """
    plan = Plan.Startup.value
    email = f"sign_up_{plan}_test@test.com"
    sign_up(email, plan)

    user = User.get_user_from_email(email, get_db_session())
    assert len(list(user.owned_workspaces)) == 2

    # The assumption is that the personal workspace is created before the paid one
    # And 'owned_workspaces' relationship is sorted by creation date DESC
    personal_workspace = user.owned_workspaces[1]
    startup_workspace = user.owned_workspaces[0]

    assert personal_workspace.plan == Plan.Personal.value
    assert personal_workspace.subscription_is_active is True

    assert startup_workspace.plan == plan
    assert startup_workspace.subscription_is_active is False

    # Let's also check that the user is added to created Workspaces
    get_db_session().query(UserWorkspace).filter(
        UserWorkspace.user_id == user.id, UserWorkspace.workspace_id == personal_workspace.id).one()
    get_db_session().query(UserWorkspace).filter(
        UserWorkspace.user_id == user.id, UserWorkspace.workspace_id == startup_workspace.id).one()

    client = _get_web_client_with_credentials(user.id, email)

    resp = client.get('/api/v1/workspaces')
    assert resp.status_code == 200
    assert len(resp.json) == 2

    # This is Personal workspace (because of the way we sort workspaces by created date)
    assert resp.json[0]['owner_id'] == str(user.id)
    assert resp.json[0]['plan'] == Plan.Personal.value
    assert resp.json[0]['subscription_is_active'] == 'True'

    # This is Startup workspace (because of the way we sort workspaces by created date)
    assert resp.json[1]['owner_id'] == str(user.id)
    assert resp.json[1]['plan'] == plan
    assert resp.json[1]['subscription_is_active'] == 'False'

    # We should only be able to upgrade Startup plan to Business
    resp = client.post(f'/api/v1/workspaces/{str(startup_workspace.id)}/upgrade/Startup')
    assert resp.status_code == 400
    resp = client.post(f'/api/v1/workspaces/{str(startup_workspace.id)}/downgrade/Startup')
    assert resp.status_code == 400
    resp = client.post(f'/api/v1/workspaces/{str(startup_workspace.id)}/downgrade/Business')
    assert resp.status_code == 400

    resp = client.post(f'/api/v1/workspaces/{str(startup_workspace.id)}/upgrade/Business')
    assert resp.status_code == 200
    get_db_session().refresh(startup_workspace)
    assert startup_workspace.plan == Plan.Business.value
    assert startup_workspace.subscription_is_active is False  # User needs to pay


def test_business(postgres):
    """
    When user is registered with "Business":
    * Personal Workspace created
    * Business workspace created (TODO make workspace name configurable)
    * Registered user becomes an owner of Personal Workspace and Business workspace
    * Private Job Templates initialized (still TODO)
    """
    plan = Plan.Business.value
    email = f"sign_up_{plan}_test@test.com"
    sign_up(email, plan)

    user = User.get_user_from_email(email, get_db_session())
    assert len(list(user.owned_workspaces)) == 2

    # The assumption is that the personal workspace is created before the paid one
    # And 'owned_workspaces' relationship is sorted by creation date DESC
    personal_workspace = user.owned_workspaces[1]
    business_workspace = user.owned_workspaces[0]

    assert personal_workspace.plan == Plan.Personal.value
    assert personal_workspace.subscription_is_active is True

    assert business_workspace.plan == plan
    assert business_workspace.subscription_is_active is False

    # Let's also check that the user is added to created Workspaces
    get_db_session().query(UserWorkspace).filter(
        UserWorkspace.user_id == user.id, UserWorkspace.workspace_id == personal_workspace.id).one()
    get_db_session().query(UserWorkspace).filter(
        UserWorkspace.user_id == user.id, UserWorkspace.workspace_id == business_workspace.id).one()

    client = _get_web_client_with_credentials(user.id, email)

    resp = client.get('/api/v1/workspaces')
    assert resp.status_code == 200
    assert len(resp.json) == 2

    # This is Personal workspace (because of the way we sort workspaces by created date)
    assert resp.json[0]['owner_id'] == str(user.id)
    assert resp.json[0]['plan'] == Plan.Personal.value
    assert resp.json[0]['subscription_is_active'] == 'True'

    # This is Business workspace (because of the way we sort workspaces by created date)
    assert resp.json[1]['owner_id'] == str(user.id)
    assert resp.json[1]['plan'] == plan
    assert resp.json[1]['subscription_is_active'] == 'False'

    # We should only be able to downgrade Business plan to Startup
    resp = client.post(f'/api/v1/workspaces/{str(business_workspace.id)}/upgrade/Startup')
    assert resp.status_code == 400
    resp = client.post(f'/api/v1/workspaces/{str(business_workspace.id)}/downgrade/Business')
    assert resp.status_code == 400
    resp = client.post(f'/api/v1/workspaces/{str(business_workspace.id)}/upgrade/Business')
    assert resp.status_code == 400

    resp = client.post(f'/api/v1/workspaces/{str(business_workspace.id)}/downgrade/Startup')
    assert resp.status_code == 200
    get_db_session().refresh(business_workspace)
    assert business_workspace.plan == Plan.Startup.value


def test_enterprise():
    """
    When user is registered with "Enterprise":
    * Extra fields while registration pop-up: "Team Name"
    * Personal Workspace created
    * {Team name} workspace created
    * Registered user becomes part of Personal Workspace and {Team name} workspace
    * User become and owner (the one who is paying for a team)
    * Private Job Templates initialized (still TODO)
    * 4 office hours with us
    """
    pass
