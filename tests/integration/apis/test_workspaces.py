import pytest
from flask.testing import FlaskClient

from core.models import get_db_session, db_commit
from core.models.workspaces import Invitation, InvitationStatus, Plan
from core.models.users_workspaces import UserWorkspace

from core.services import workspace as service
from core.services import user as user_service

from application import application


@pytest.fixture(scope='module')
def invitee_email():
    return 'somebody@seamlesscloud.io'


@pytest.fixture(scope='module')
def invitee_id(invitee_email):
    user_id = user_service.sign_up(invitee_email)
    return user_id


@pytest.fixture(scope='module')
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


def test_invite_user(web_client, workspace_id, invitee_email):
    url = f'/api/v1/workspaces/{workspace_id}/invite/{invitee_email}'
    res = web_client.get(url)
    assert res.status_code == 200

    session = get_db_session()

    invitation = session.query(Invitation).filter_by(workspace_id=workspace_id, user_email=invitee_email).one_or_none()
    assert invitation, "We should have Invitation object created"
    assert invitation.status == InvitationStatus.pending.value, \
        "Invitation object should be created with `pending` status"


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


@pytest.fixture
def intercepted_invitee_email():
    return 'seombody_whos_email_is_hacked@seamlesscloud.io'


@pytest.fixture
def intercepted_invitee_id(intercepted_invitee_email):
    user_id = user_service.sign_up(intercepted_invitee_email)
    return user_id


@pytest.fixture
def intercepted_invitation_id(intercepted_invitee_email, workspace_id):
    session = get_db_session()

    invitation = Invitation(
        user_email=intercepted_invitee_email,
        workspace_id=workspace_id
    )
    session.add(invitation)
    db_commit()

    return invitation.id


def test_invite_accepted_wrong_user_or_workspace(web_client, intercepted_invitation_id, workspace_id,
                                                 intercepted_invitee_id, intercepted_invitee_email, invitee_web_client):
    """
    When request to `workspaces/accept` was made from a different user to whom invite was sent
    """
    # ensure that we hadn't user in the workspace before
    session = get_db_session()
    user_workspace = session.query(UserWorkspace).filter_by(workspace_id=workspace_id,
                                                            user_id=intercepted_invitee_id).one_or_none()
    assert not user_workspace, "UserWorkspace object should not be created at the start of this test"

    # WRONG USER, CORRECT WORKSPACE_ID SCENARIO
    url = f'/api/v1/workspaces/{workspace_id}/accept/{intercepted_invitation_id}'
    res = web_client.get(url)  # we use defailt `web_client` where `user_id` is used, but not `intercepted_invitee_id`
    assert res.status_code == 400, "Different user should see 400 error " \
                                   "because the user accepting is not the one the invitation was sent to"

    invitation = session.query(Invitation).filter_by(workspace_id=workspace_id,
                                                     user_email=intercepted_invitee_email).one()
    assert invitation.status == InvitationStatus.pending.value, "Invitation status should still be pending"

    user_workspace = session.query(UserWorkspace).filter_by(workspace_id=workspace_id,
                                                            user_id=intercepted_invitee_id).one_or_none()
    assert not user_workspace, "We should have no UserWorkspace record created"

    # RIGHT USER, INCORRECT WORKSPACE_ID SCENARIO
    wrong_workspace_id = '987654321'
    url = f'/api/v1/workspaces/{wrong_workspace_id}/accept/{intercepted_invitation_id}'
    res = invitee_web_client.get(url)  # we use the web client with the correct user, but we pass a wrong workspace_id
    assert res.status_code == 404, "We should see error because the workspace_id does not exist"
    # TODO add a scenario when workspace exists but does not match the one in the invitation

    invitation = session.query(Invitation).filter_by(workspace_id=workspace_id,
                                                     user_email=intercepted_invitee_email).one()
    assert invitation.status == InvitationStatus.pending.value, "Invitation status should still be pending"

    user_workspace = session.query(UserWorkspace).filter_by(workspace_id=workspace_id,
                                                            user_id=intercepted_invitee_id).one_or_none()
    assert not user_workspace, "We should have no UserWorkspace record created"


def test_user_invitation_flow(web_client, invitee_web_client, invitation_id, workspace_id, invitee_id, invitee_email):
    url = f'/api/v1/workspaces/{workspace_id}/accept/{invitation_id}'

    # ensure that we hadn't user in the workspace before
    session = get_db_session()
    user_workspace = session.query(UserWorkspace).filter_by(workspace_id=workspace_id,
                                                            user_id=invitee_id).one_or_none()
    assert not user_workspace, "UserWorkspace object should not be created at the start of this test"

    res = invitee_web_client.get(url)
    assert res.status_code == 200
    invitation = session.query(Invitation).filter_by(workspace_id=workspace_id, user_email=invitee_email).one()
    assert invitation.status == InvitationStatus.accepted.value, "Invitation status should be accepted"

    user_workspace = session.query(UserWorkspace).filter_by(workspace_id=workspace_id,
                                                            user_id=invitee_id).one_or_none()
    assert user_workspace, "We should have one record of UserWorkspace created"

    # Now let's try to accept the invitation one more time
    res = invitee_web_client.get(url)
    assert res.status_code == 400, \
        "User should receive 400 - Bad Request error code when inviting users already in the workspace"

    # ensure that we have UserWorkspace entry created for `invitee_id` and `workspace_id`
    session = get_db_session()
    assert session.query(UserWorkspace).filter_by(user_id=invitee_id, workspace_id=workspace_id).one_or_none()

    url = f'/api/v1/workspaces/{workspace_id}/remove/{invitee_email}'
    res = web_client.get(url)
    assert res.status_code == 200

    assert not session.query(UserWorkspace).filter_by(user_id=invitee_id, workspace_id=workspace_id).one_or_none(), \
        "UserWorkspace entry should not exist after we removed user from the workspace"


@pytest.mark.skip(reason='not implemented yet')
def test_remove_user_from_workspace_not_permitted():
    """
    User other then owner of the workspace or the user itself cannot remove other users from workspace
    """
    pass


@pytest.mark.skip(reason='not implemented yet')
def test_invite_not_owner():
    """
    Only owner has a permission to invite users to workspace
    """
    pass


@pytest.mark.skip(reason='not implemented yet')
def test_invite_again():
    """
    # TODO: we need to come up with a logic to limit number of invitations owner can send to user in some time period
    Logic of sending out repeated invitations
    """
    pass
