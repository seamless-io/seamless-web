"""

Revision ID: 951e3f4e8d47
Revises: 101b182bd0ce
Create Date: 2020-07-16 13:24:06.550961

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '951e3f4e8d47'
down_revision = '101b182bd0ce'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('jobs', sa.Column('aws_cron', sa.Text(), nullable=True))
    op.add_column('jobs', sa.Column('cron', sa.Text(), nullable=True))
    op.add_column('jobs', sa.Column('human_cron', sa.Text(), nullable=True))
    op.drop_column('jobs', 'schedule')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('jobs', sa.Column('schedule', sa.TEXT(), autoincrement=False, nullable=True))
    op.drop_column('jobs', 'human_cron')
    op.drop_column('jobs', 'cron')
    op.drop_column('jobs', 'aws_cron')
    # ### end Alembic commands ###
