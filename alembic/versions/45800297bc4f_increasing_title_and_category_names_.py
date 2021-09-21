"""increasing title and category names lenght

Revision ID: 45800297bc4f
Revises: 2fc7aa4d249f
Create Date: 2021-08-04 18:33:32.064405

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '45800297bc4f'
down_revision = '2fc7aa4d249f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('categories', 'category_name',
               existing_type=sa.VARCHAR(length=40),
               type_=sa.String(length=80),
               existing_nullable=False)
    op.alter_column('titles', 'title_name',
               existing_type=sa.VARCHAR(length=40),
               type_=sa.String(length=150),
               existing_nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('titles', 'title_name',
               existing_type=sa.String(length=150),
               type_=sa.VARCHAR(length=40),
               existing_nullable=False)
    op.alter_column('categories', 'category_name',
               existing_type=sa.String(length=80),
               type_=sa.VARCHAR(length=40),
               existing_nullable=False)
    # ### end Alembic commands ###
