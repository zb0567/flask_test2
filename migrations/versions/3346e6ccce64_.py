"""empty message

Revision ID: 3346e6ccce64
Revises: ab698630487d
Create Date: 2020-04-19 00:30:49.204475

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3346e6ccce64'
down_revision = 'ab698630487d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('posts', schema=None) as batch_op:
        batch_op.add_column(sa.Column('body_html', sa.Text(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('posts', schema=None) as batch_op:
        batch_op.drop_column('body_html')

    # ### end Alembic commands ###
