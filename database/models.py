"""DB entities"""
import typing

from random import randint

import sqlalchemy as sa
from gino import Gino
from sqlalchemy import and_

from database.utilities import CategoryRating, parse_results, get_required_categories

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
    email_confirmed = sa.Column(sa.Boolean(), nullable=True, default=False)

    @classmethod
    async def get_users_top_categories_id(
            cls,
            amount_of_categories: int,
            user_id: int,
    ) -> list['CategoryRating']:
        """Get users top categories"""
        all_categories_ids = await Category.get_all_available_categories_ids()
        rated_categories = await db.select(
            [Rating.category_type_id, Rating.rating_number]
        ).select_from(
            cls.join(Rating)
        ).gino.query.where(
            and_(
                Rating.rating_number >= 0,
                cls.id == user_id,
            )
        ).order_by(
            Rating.rating_number
        ).gino.all()
        return parse_results(amount_of_categories, rated_categories, all_categories_ids)

    @classmethod
    async def get_new_users_categories_id(
            cls,
            amount_of_categories: int,
            user_id: int,
    ) -> list['CategoryRating']:
        """Get users new categories"""
        all_categories_ids = await Category.get_all_available_categories_ids()
        unparsed_unrated_categories_ids = await db.select(
            [
                Rating.category_type_id,
                Rating.rating_number,
            ]
        ).select_from(
            cls.join(Rating)
        ).gino.query.where(
            cls.id == user_id
        ).gino.all()
        if len(all_categories_ids) - len(unparsed_unrated_categories_ids) >= amount_of_categories:
            result = []
            get_required_categories(unparsed_unrated_categories_ids, all_categories_ids, amount_of_categories)
            for unparsed_category in unparsed_unrated_categories_ids:
                result.append(CategoryRating(unparsed_category[0], 0))
            return result
        zero_rated_categories = await db.select(
            [Rating.category_type_id, Rating.rating_number]
        ).select_from(
            cls.join(Rating)
        ).gino.query.where(
            and_(
                Rating.rating_number == 0,
                cls.id == user_id,
            )
        ).gino.all()
        return parse_results(amount_of_categories, zero_rated_categories, all_categories_ids)

    @classmethod
    async def get_user_by_username(cls, username: str) -> typing.Optional['User']:
        """Get user from db by username"""
        user = await cls.query.where(User.username == username).gino.one_or_none()
        return user

    @classmethod
    async def get_user_by_email(cls, email: str) -> typing.Optional['User']:
        """Get user from db by email"""
        user = await cls.query.where(User.email == email).gino.one_or_none()
        return user

    @classmethod
    async def check_if_user_already_exist(cls, username: str, email: str) -> bool:
        """Check if given username or email already exist in db"""
        result = await db.select(
            [cls.email, cls.username]
        ).select_from(cls).gino.query.where(
            and_(
                cls.username == username,
                cls.email == email
            )
        ).gino.one_or_none()
        if result:
            return True
        return False

    @classmethod
    async def get_all_telegram_users(cls) -> list['User']:
        """Get all telegram users from db"""
        users = await cls.query.where(cls.telegram_id > 0).gino.all()
        return users


class Category(db.Model):
    __tablename__ = 'categories'

    id = sa.Column(sa.Integer(), primary_key=True)
    category_name = sa.Column(sa.String(80), unique=True, nullable=False)

    @classmethod
    async def get_category_by_name(cls, category_name: str) -> typing.Optional['Category']:
        """Get category by its name if it exist"""
        category = await cls.query.where(cls.category_name == category_name).gino.one_or_none()
        return category

    @classmethod
    async def get_all_available_categories_ids(cls) -> list[int]:
        """Get list with all available categories in db"""
        result = []
        categories = await cls.select('id').gino.all()
        for data in categories:
            result.append(data[0])
        return result


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
    title_name = sa.Column(sa.String(150), nullable=False)
    title_rating = sa.Column(sa.Float(), default=0, nullable=False)
    amount_of_likes = sa.Column(sa.Float(), default=0, nullable=False)
    amount_of_views = sa.Column(sa.Integer(), default=0, nullable=False)

    @classmethod
    async def get_amount_of_titles_by_type(cls, title_type: int) -> int:
        """Get all amount of titles by its category"""
        amount_of_titles = await cls.select().where(cls.title_type_id == title_type).count().gino.scalar()
        return amount_of_titles

    @classmethod
    async def get_all_titles_id_by_category(cls, title_type: int) -> list[int]:
        """Get all title ids for one category"""
        result = []
        raw_result = await cls.select('id').where(cls.title_type_id == title_type).gino.all()
        for data in raw_result:
            result.append(data[0])
        return result

    @classmethod
    async def get_random_title_by_category(cls, title_type: int) -> 'Title':
        """Get one title by its category"""
        title_ids = await cls.get_all_titles_id_by_category(title_type)
        title = await cls.get(title_ids[randint(0, len(title_ids)-1)])
        return title
