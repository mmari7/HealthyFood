import datetime
import sqlalchemy
from sqlalchemy import orm
from werkzeug.security import generate_password_hash, check_password_hash
from .db_session import SqlAlchemyBase


class Relation(SqlAlchemyBase):
    __tablename__ = 'relations'

    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"), nullable=False, primary_key=True)
    recipe_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("recipes.id"), nullable=False, primary_key=True)

