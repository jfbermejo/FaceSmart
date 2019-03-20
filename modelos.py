import datetime
from flask_login import UserMixin
from flask_bcrypt import generate_password_hash
from peewee import *

DATABASE = SqliteDatabase('social.db')


class User(UserMixin, Model):
    username = CharField(unique=True)
    email = CharField(unique=True)
    password = CharField(max_length=25)
    joined_at = DateTimeField(default=datetime.datetime.now)

    class Meta:
        database = DATABASE
        order_by = '-joined_at'

    # Creamos un método de la clase para crear el usuario invocando desde la clase
    @classmethod
    def create_user(cls, username, email, password):
        try:
            cls.create(
                username = username,
                email = email,
                password = generate_password_hash(password),
            )
        except IntegrityError:
            # raise ValueError('User already exists')
            pass


def initialize():
    DATABASE.connect()
    DATABASE.create_tables([User], safe=True)
    DATABASE.close()