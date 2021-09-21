"""first migration

Revision ID: 1d1f25510179
Revises: 
Create Date: 2021-06-15 17:43:56.985547

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1d1f25510179'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('biology_titles',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title_name', sa.String(length=40), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('chemistry_titles',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title_name', sa.String(length=40), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('history_titles',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title_name', sa.String(length=40), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('it_titles',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title_name', sa.String(length=40), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('physics_titles',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title_name', sa.String(length=40), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=30), nullable=False),
    sa.Column('password', sa.String(length=70), nullable=False),
    sa.Column('telegram_id', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('telegram_id'),
    sa.UniqueConstraint('username')
    )
    op.create_table('rating_types',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('subject_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('rating_number', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('rating_types')
    op.drop_table('users')
    op.drop_table('physics_titles')
    op.drop_table('it_titles')
    op.drop_table('history_titles')
    op.drop_table('chemistry_titles')
    op.drop_table('biology_titles')
    # ### end Alembic commands ###
