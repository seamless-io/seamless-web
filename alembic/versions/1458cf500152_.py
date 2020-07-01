"""

Revision ID: 1458cf500152
Revises: 82045e42b0bd
Create Date: 2020-07-01 11:26:34.599889

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1458cf500152'
down_revision = '82045e42b0bd'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('job_runs', sa.Column('status', sa.Text(), nullable=False))
    op.drop_column('job_runs', 'result')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('job_runs', sa.Column('result', sa.TEXT(), autoincrement=False, nullable=False))
    op.drop_column('job_runs', 'status')
    # ### end Alembic commands ###