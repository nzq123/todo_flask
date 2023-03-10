"""third  migration

Revision ID: 3eeff246b482
Revises: f5a08253f30f
Create Date: 2023-02-23 19:35:46.720172

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3eeff246b482'
down_revision = 'f5a08253f30f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('todo', schema=None) as batch_op:
        batch_op.add_column(sa.Column('user_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(batch_op.f('fk_todo_user_id_users'), 'users', ['user_id'], ['id'])

    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.create_unique_constraint(batch_op.f('uq_users_login'), ['login'])
        batch_op.drop_column('desc')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('desc', sa.VARCHAR(), nullable=False))
        batch_op.drop_constraint(batch_op.f('uq_users_login'), type_='unique')

    with op.batch_alter_table('todo', schema=None) as batch_op:
        batch_op.drop_constraint(batch_op.f('fk_todo_user_id_users'), type_='foreignkey')
        batch_op.drop_column('user_id')

    # ### end Alembic commands ###
