"""empty message

Revision ID: cc582b40f51b
Revises: 61ae663d9a97
Create Date: 2024-10-27 18:04:10.595145

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cc582b40f51b'
down_revision = '61ae663d9a97'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('otp', sa.String(length=225), nullable=False))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('otp')

    # ### end Alembic commands ###