"""DB entities"""
import typing
from random import randint

import sqlalchemy as sa
from gino import Gino
from sqlalchemy import and_

db = Gino()  # DB initialization


async def connect_to_db(uri: str):
    await db.set_bind(uri)


class User(db.Model):
    __tablename__ = 'users'

    id = sa.Column(sa.Integer(), primary_key=True)
    username = sa.Column(sa.String(30), nullable=False, unique=True)
    password = sa.Column(sa.String(150), nullable=False)
    telegram_id = sa.Column(sa.Integer(), nullable=True, unique=True)
    email = sa.Column(sa.String(30), nullable=False, unique=True)

    @classmethod
    async def get_user_by_username(cls, username: str) -> typing.Optional['User']:
        """Get user from db by username"""
        user = await cls.query.where(User.username == username).gino.one_or_none()
        return user

    @classmethod
    async def get_user_by_email(cls, email: str) -> typing.Optional['User']:
        user = await cls.query.where(User.email == email).gino.one_or_none()
        return user

    @classmethod
    async def get_all_telegram_users(cls) -> list['User']:
        """Get all telegram users from db"""
        users = await cls.query.where(cls.telegram_id > 0).gino.all()
        return users


class Category(db.Model):
    __tablename__ = 'categories'

    id = sa.Column(sa.Integer(), primary_key=True)
    category_name = sa.Column(sa.String(40), unique=True, nullable=False)


class Rating(db.Model):
    __tablename__ = 'ratings'

    id = sa.Column(sa.Integer(), primary_key=True)
    category_type_id = sa.Column(sa.Integer(), sa.ForeignKey(Category.id, ondelete='CASCADE'), nullable=False)
    user_id = sa.Column(sa.Integer(), sa.ForeignKey(User.id, ondelete='CASCADE'), nullable=False)
    rating_number = sa.Column(sa.Integer(), default=0, nullable=False)

    @classmethod
    async def get_user_theme_rating(cls, category_type_id: int, username: str) -> typing.Optional['Rating']:
        """Get users theme like rating"""
        user = await User.get_user_by_username(username)
        result = await cls.join(User).select().where(
            and_(
                cls.category_type_id == category_type_id,
                cls.user_id == user.id,
            ),
        ).gino.one_or_none()
        return result


class Title(db.Model):
    __tablename__ = 'titles'

    id = sa.Column(sa.Integer(), primary_key=True)
    title_type_id = sa.Column(sa.Integer(), sa.ForeignKey(Category.id, ondelete='CASCADE'), nullable=False)
    title_name = sa.Column(sa.String(40), nullable=False)
    title_rating = sa.Column(sa.Float(), default=0, nullable=False)
    amount_of_likes = sa.Column(sa.Float(), default=0, nullable=False)
    amount_of_views = sa.Column(sa.Integer(), default=0, nullable=False)

    @classmethod
    async def get_amount_of_titles_by_type(cls, title_type: int) -> int:
        """Get all amount of titles by its category"""
        amount_of_titles = cls.select().where(cls.title_type_id == title_type).count().gino.scalar()
        return amount_of_titles

    @classmethod
    async def get_random_title_by_category(cls, title_type: int) -> 'Title':
        """Get one title by its category"""
        amount_of_titles = await cls.get_amount_of_titles_by_type(title_type)
        title = await cls.select().where(
            and_(
                cls.title_type_id == title_type,
                cls.id == randint(0, amount_of_titles),
            ),
        ).gino.first()
        return title
