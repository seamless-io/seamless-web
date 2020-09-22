import pytest

from core.models import get_db_session
from core.models.workspaces import Invitation, InvitationStatus, Plan

from core.services import workspace as service


@pytest.fixture
def workspace_id(user_id):
    return service.create_workspace(user_id, Plan.Personal)


@pytest.fixture
def invitee_email():
    return 'somebody@seamlesscloud.io'


@pytest.mark.xfail(reason='not implemented yet')
def test_invite_user(web_client, workspace_id, invitee_email):
    url = f'/api/v1/workspaces/{workspace_id}/invite/{invitee_email}'
    res = web_client.get(url)
    assert res.status_code == 200

    session = get_db_session()

    invitation = session.query(Invitation).filter_by(workspace_id=workspace_id, user_email=invitee_email).one()
    assert invitation.status == InvitationStatus.pending.value


def test_user_accept_invitation(web_client):
    pass


def test_remove_user_from_workspace():
    pass


def test_invite_again():
    pass
