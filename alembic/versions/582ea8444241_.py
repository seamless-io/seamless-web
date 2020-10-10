"""empty message

Revision ID: 582ea8444241
Revises: d09ae02e17a5
Create Date: 2020-10-08 21:19:59.339607

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '582ea8444241'
down_revision = 'd09ae02e17a5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('payment_method_id', sa.Text(), nullable=True))
    op.create_unique_constraint('uq_users_customer_id', 'users', ['customer_id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('uq_users_customer_id', 'users', type_='unique')
    op.drop_column('users', 'payment_method_id')
    # ### end Alembic commands ###