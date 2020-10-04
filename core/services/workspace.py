from core.models import get_db_session

from core.models.workspaces import Workspace


def get_default_workspace(user_id: str):
    session = get_db_session()

    # default workspace will be personal, until we figure out how to setup preferences
    workspace = session.query(Workspace).filter_by(owner_id=user_id, personal=True).one()

    return workspace
