"""DB entities"""
from gino import Gino
import sqlalchemy as sa


db = Gino()  # DB initialization


async def connect_to_db(uri: str):
    await db.set_bind(uri)


class User(db.Model):
    __tablename__ = 'users'

    id = sa.Column(sa.Integer(), primary_key=True)
    username = sa.Column(sa.String(30), nullable=False, unique=True)
    password = sa.Column(sa.String(40), nullable=False)
    telegram_id = sa.Column(sa.Integer(), nullable=True, unique=True)


class Rating(db.Model):
    __tablename__ = 'ratings'

    PHYSICS = 0
    CHEMISTRY = 1
    BIOLOGY = 2
    HISTORY = 3
    IT = 4

    id = sa.Column(sa.Integer(), primary_key=True)
    subject_id = sa.Column(sa.Integer(), nullable=False)
    user_id = sa.Column(sa.Integer(), sa.ForeignKey(User.id, ondelete='CASCADE'), nullable=False)
    rating_number = sa.Column(sa.Integer(), default=0, nullable=False)


class PhysicsTitle(db.Model):
    __tablename__ = 'physics_titles'

    id = sa.Column(sa.Integer(), primary_key=True)
    title_name = sa.Column(sa.String(40), nullable=False)


class ChemistryTitle(db.Model):
    __tablename__ = 'chemistry_titles'

    id = sa.Column(sa.Integer(), primary_key=True)
    title_name = sa.Column(sa.String(40), nullable=False)


class BiologyTitle(db.Model):
    __tablename__ = 'biology_titles'

    id = sa.Column(sa.Integer(), primary_key=True)
    title_name = sa.Column(sa.String(40), nullable=False)


class HistoryTitle(db.Model):
    __tablename__ = 'history_titles'

    id = sa.Column(sa.Integer(), primary_key=True)
    title_name = sa.Column(sa.String(40), nullable=False)


class ItTitle(db.Model):
    __tablename__ = 'it_titles'

    id = sa.Column(sa.Integer(), primary_key=True)
    title_name = sa.Column(sa.String(40), nullable=False)