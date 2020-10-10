"""empty message

Revision ID: a84c3eea9237
Revises: 26471a2a0a1c
Create Date: 2020-10-10 01:25:11.166992

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a84c3eea9237'
down_revision = '26471a2a0a1c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('job_usages',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('subscription_item_id', sa.Text(), nullable=False),
    sa.Column('job_id', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['job_id'], ['jobs.id'], ),
    sa.ForeignKeyConstraint(['subscription_item_id'], ['subscription_items.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.add_column('jobs', sa.Column('became_chargeable', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('jobs', 'became_chargeable')
    op.drop_table('job_usages')
    # ### end Alembic commands ###