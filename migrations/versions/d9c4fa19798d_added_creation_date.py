"""added creation date

Revision ID: d9c4fa19798d
Revises: b2be6186e53b
Create Date: 2018-12-14 09:00:10.481627

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd9c4fa19798d'
down_revision = 'b2be6186e53b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('reviews', sa.Column('creationdate', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('reviews', 'creationdate')
    # ### end Alembic commands ###
