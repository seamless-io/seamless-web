from core.models import get_db_session, db_commit

from core.models.workspaces import Workspace


def get_default_workspace(user_id: int):
    session = get_db_session()

    # default workspace will be personal, until we figure out how to setup preferences
    workspace = session.query(Workspace).filter_by(owner_id=user_id, personal=True).one()

    return workspace


def create(user_id: int, name: str):
    session = get_db_session()

    workspace = Workspace(owner_id=user_id, name=name)

    session.add(workspace)
    db_commit()

    return workspace.id


def delete(workspace_id: int):
    session = get_db_session()

    session.query(Workspace).filter_by(id=workspace_id).delete()

    db_commit()
