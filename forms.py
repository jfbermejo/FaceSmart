from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, ValidationError, Email, Regexp, Length, EqualTo

from modelos import User


def name_exists(form, field):
    if User.select().where(User.username == field.data).exists():
        raise ValidationError('Ya existe un usuario con ese nombre')


def email_exists(form, field):
    if User.select().where(User.email == field.data).exists():
        raise ValidationError('Usuario con ese email ya existe')


class RegisterForm(FlaskForm): # hereda de FlaskForm
    # Atributos son los campos que el usuario deberá rellenar
    username = StringField(
        'Username',
        validators=[
            DataRequired(),
            Regexp(
                r'^[a-zA-Z0-9_]+$'
            ),
            name_exists
        ]
    )

    email = StringField(
        'Email',
        validators=[
            DataRequired(),
            Email(),
            email_exists
        ]
    )

    password = PasswordField(
        'Password',
        validators=[
            DataRequired(),
            Length(min=4),
            EqualTo('password2', message='Los passwords deben coincidir')
        ]
    )

    password2 = PasswordField(
        'Confirm Password',
        validators=[
            DataRequired(),
        ]
    )
