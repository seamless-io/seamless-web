"""

Revision ID: 9e3070bd7c87
Revises: 9eece4620cb6
Create Date: 2020-08-31 19:21:52.358247

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9e3070bd7c87'
down_revision = '9eece4620cb6'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('job_templates',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.Text(), nullable=False),
    sa.Column('short_description', sa.Text(), nullable=False),
    sa.Column('long_description_url', sa.Text(), nullable=False),
    sa.Column('tags', sa.Text(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_job_templates_name'), 'job_templates', ['name'], unique=True)
    op.add_column('jobs', sa.Column('job_template_id', sa.Integer(), nullable=True))
    op.create_foreign_key('jobs_job_template_id_fkey', 'jobs', 'job_templates', ['job_template_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('jobs_job_template_id_fkey', 'jobs', type_='foreignkey')
    op.drop_column('jobs', 'job_template_id')
    op.drop_index(op.f('ix_job_templates_name'), table_name='job_templates')
    op.drop_table('job_templates')
    # ### end Alembic commands ###
