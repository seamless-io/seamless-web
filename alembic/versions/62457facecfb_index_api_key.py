"""index_api_key

Revision ID: 62457facecfb
Revises: 6ec63ca907e6
Create Date: 2020-06-30 09:19:07.838045

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '62457facecfb'
down_revision = '6ec63ca907e6'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index(op.f('ix_users_api_key'), 'users', ['api_key'], unique=True)
    op.drop_constraint('users_api_key_key', 'users', type_='unique')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint('users_api_key_key', 'users', ['api_key'])
    op.drop_index(op.f('ix_users_api_key'), table_name='users')
    # ### end Alembic commands ###