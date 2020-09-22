import pytest

from core.models import get_db_session, db_commit
from core.models.workspaces import Invitation, InvitationStatus, Plan
from core.models.users_workspaces import UserWorkspace

from core.services import workspace as service
from core.services import user as user_service


@pytest.fixture
def invitee_email():
    return 'somebody@seamlesscloud.io'


@pytest.fixture
def invitee_id(invitee_email):
    user_id = user_service.sign_up(invitee_email)
    return user_id


@pytest.fixture
def invitee_web_client(postgres, invitee_id, invitee_email):
    """
    Web client fixture. This fixture should be used when we are testing API used by the frontend and complying
    with auth0 authentication
    """
    application.config['TESTING'] = True
    # This is a default class, but we need to explicitly set it because cli_client overwrites it
    application.test_client_class = FlaskClient

    with application.test_client() as client:
        with client.session_transaction() as session:
            session['jwt_payload'] = session['profile'] = {
                'auth0_user_id': invitee_id,  # no matter what is in here
                'email': invitee_email,
                'user_id': invitee_id
            }
        yield client


@pytest.fixture
def workspace_id(user_id):
    return service.create_workspace(user_id, Plan.Personal)


@pytest.mark.xfail(reason='not implemented yet')
def test_invite_user(web_client, workspace_id, invitee_email):
    url = f'/api/v1/workspaces/{workspace_id}/invite/{invitee_email}'
    res = web_client.get(url)
    assert res.status_code == 200

    session = get_db_session()

    invitation = session.query(Invitation).filter_by(workspace_id=workspace_id, user_email=invitee_email).one()
    assert invitation.status == InvitationStatus.pending.value


@pytest.fixture
def invitation_id(invitee_email, workspace_id):
    session = get_db_session()

    invitation = Invitation(
        user_email=invitee_email,
        workspace_id=workspace_id
    )
    session.add(invitation)
    db_commit()

    return invitation.id


def test_invite_accepted_by_wrong_user():
    """
    When request to `workspaces/accept` was made from a different user to whom invite was sent
    """
    pass


@pytest.mark.xfail(reason='not implemented yet')
def test_user_accept_invitation(invitee_web_client, invitation_id, workspace_id, invitee_id):
    url = f'/api/v1/workspaces/{workspace_id}/accept/{invitation_id}'

    res = invitee_web_client.get(url)
    assert res.status_code == 200

    session = get_db_session()

    user_workspace = session.query(UserWorkspace).filter_by(workspace_id=workspace_id, user_id=invitee_id).one()
    assert user_workspace, "We should have one record of UserWorkspace created"


@pytest.mark.xfail(reason='not implemented yet')
def test_remove_user_from_workspace():
    pass


@pytest.mark.xfail(reason='not implemented yet')
def test_invite_again():
    pass



def test_invite_youself():
    pass
