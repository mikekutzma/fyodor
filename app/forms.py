from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    DecimalField,
    FormField,
    PasswordField,
    SelectField,
    StringField,
    SubmitField,
)
from wtforms.validators import (
    DataRequired,
    Email,
    EqualTo,
    ValidationError,
)
from app.models import Service, User


class RPCForm(FlaskForm):
    service = SelectField(
        "Service",
        choices=[(service.name, service.name) for service in Service.query.all()],
    )
    command = SelectField(
        "Command",
        choices=[
            (command.name, command.name)
            for command in Service.query.first().commands.all()
        ],
    )
    params = None


def get_param_form(params):
    class F(FlaskForm):
        pass

    for param in params:
        setattr(F, param.name, DecimalField(param.name, validators=[DataRequired()]))

    return FormField(F)


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Remember Me")
    submit = SubmitField("Sign In")


class UserRegistrationForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    password2 = PasswordField(
        "Repeat Password", validators=[DataRequired(), EqualTo("password")]
    )
    submit = SubmitField("Register")

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError("Please use a different username.")

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError("Please use a different email.")
