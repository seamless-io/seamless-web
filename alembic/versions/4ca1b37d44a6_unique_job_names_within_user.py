"""unique_job_names_within_user

Revision ID: 4ca1b37d44a6
Revises: 6a9295655625
Create Date: 2020-06-27 09:08:04.766674

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4ca1b37d44a6'
down_revision = '6a9295655625'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint('job_names_must_be_unique_within_user', 'jobs', ['user_id', 'name'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('job_names_must_be_unique_within_user', 'jobs', type_='unique')
    # ### end Alembic commands ###
