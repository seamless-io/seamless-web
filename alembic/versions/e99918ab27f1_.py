"""empty message

Revision ID: e99918ab27f1
Revises: d09ae02e17a5
Create Date: 2020-10-07 01:07:25.232001

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e99918ab27f1'
down_revision = 'd09ae02e17a5'
branch_labels = None
depends_on = None


def upgrade():
    op.create_unique_constraint('uq_users_customer_id', 'users', ['customer_id'])
    op.create_table(
        'subscriptions',
        sa.Column('id', sa.Text(), nullable=False),
        sa.Column('customer_id', sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(['customer_id'], ['users.customer_id'], name='fk_subscriptions_customer_id_users_customer_id'),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('subscriptions')
    op.drop_constraint('uq_users_customer_id', 'users', type_='unique')
