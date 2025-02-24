import datetime
import sqlalchemy
from sqlalchemy import orm
from werkzeug.security import generate_password_hash, check_password_hash
from .db_session import SqlAlchemyBase


class Recipe(SqlAlchemyBase):
    __tablename__ = 'recipes'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True, unique=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    category = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    time = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    portions = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    ingridients = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    steps = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    photos = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    video = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    users = orm.relationship(
        'User',
        secondary='relations',
        back_populates='recipes')



