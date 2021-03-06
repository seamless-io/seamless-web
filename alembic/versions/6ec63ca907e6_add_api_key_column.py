"""add api_key column

Revision ID: 6ec63ca907e6
Revises: 4ca1b37d44a6
Create Date: 2020-06-27 20:52:59.799512

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6ec63ca907e6'
down_revision = '4ca1b37d44a6'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('api_key', sa.String(length=20), nullable=False))
    op.create_unique_constraint(None, 'users', ['api_key'])
    op.drop_column('users', 'password_hash')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('password_hash', sa.VARCHAR(length=128), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'users', type_='unique')
    op.drop_column('users', 'api_key')
    # ### end Alembic commands ###
