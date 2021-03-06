"""

Revision ID: 943010596e91
Revises: e58765978b3b
Create Date: 2020-07-27 21:46:04.833249

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '943010596e91'
down_revision = 'e58765978b3b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('jobs', sa.Column('entrypoint', sa.Text(), nullable=True))
    op.add_column('jobs', sa.Column('requirements', sa.Text(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('jobs', 'requirements')
    op.drop_column('jobs', 'entrypoint')
    # ### end Alembic commands ###
