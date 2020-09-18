from sqlalchemy import Column, Integer, ForeignKey

from core.models.base import base


class UserWorkspace(base):
    __tablename__ = 'users_workspaces'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    workspace_id = Column(Integer, ForeignKey('workspaces.id'))

    def __repr__(self):
        return '<UserWorkspace id: %r user_id: %r workspace_id: %r>' \
               % (self.id, self.user_id, self.workspace_id)
