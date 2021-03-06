"""

Revision ID: 291fcbbed56d
Revises: e334781590f1
Create Date: 2020-10-04 20:25:59.637196

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '291fcbbed56d'
down_revision = 'e334781590f1'
branch_labels = None
depends_on = None

JOBS_WORKSPACES_FK = 'fk_jobs_workspace_id_workspaces'


def upgrade():
    # creating a workspace table
    op.create_table(
        'workspaces',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('owner_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.Text(), nullable=False),
        sa.Column('personal', sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # creating workspace for each user
    conn = op.get_bind()
    res = conn.execute('select id from users')
    for value in res:
        conn.execute(f"insert into workspaces (owner_id, name, personal) values ({value[0]}, 'Personal', true)")

    # creating nullable `workspace_id` column in a job table
    op.add_column('jobs', sa.Column('workspace_id', sa.Integer(), nullable=True))

    # populating `workspace_id` fields with recently created workspaces (via user)
    res = conn.execute("select id, owner_id from workspaces")
    for value in res:
        conn.execute(f"update jobs set workspace_id={value[0]} where user_id={value[1]}")

    # make `workspace_id` not null column (we should not have jobs without workspaces)
    op.alter_column('jobs', 'workspace_id', existing_type=sa.INTEGER(), nullable=False)
    op.create_foreign_key(JOBS_WORKSPACES_FK, 'jobs', 'workspaces', ['workspace_id'], ['id'], ondelete='CASCADE')


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(JOBS_WORKSPACES_FK, 'jobs', type_='foreignkey')
    op.drop_column('jobs', 'workspace_id')
    op.drop_table('workspaces')
    # ### end Alembic commands ###
