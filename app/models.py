import base64
import secrets

from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


def gen_api_key():
    return secrets.token_hex(64)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    is_approved = db.Column(db.Boolean, default=False)
    is_admin = db.Column(db.Boolean, default=False)
    api_key = db.Column(db.String(64), default=gen_api_key)

    def __repr__(self):
        return "<User {}>".format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def approve(self):
        self.is_approved = True


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


@login.request_loader
def load_user_from_request(request):

    # first, try to login using the api_key url arg
    api_key = request.headers.get("api_key")
    if api_key:
        user = User.query.filter_by(api_key=api_key).first()
        if user:
            return user

    # next, try to login using Basic Auth
    api_key = request.headers.get("Authorization")
    if api_key:
        api_key = api_key.replace("Basic ", "", 1)
        try:
            api_key = base64.b64decode(api_key)
        except TypeError:
            pass
        user = User.query.filter_by(api_key=api_key).first()
        if user:
            return user

    # finally, return None if both methods did not login the user
    return None


class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(16), unique=True)
    name = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    commands = db.relationship("Command", backref="service", lazy="dynamic")

    def __repr__(self):
        return f"<Service {self.name}>"

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Command(db.Model):
    __table_args__ = (
        db.UniqueConstraint(
            "service_id", "name", name="unique_command_name_per_service"
        ),
        db.UniqueConstraint(
            "service_id", "method", "target", name="unique_target_method_per_service"
        ),
    )
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)
    method = db.Column(db.String(6))
    target = db.Column(db.String(128))
    service_id = db.Column(db.Integer, db.ForeignKey("service.id"))
    params = db.relationship("Param", backref="command", lazy="dynamic")

    def __repr__(self):
        return f"<Command {self.name}>"


class Param(db.Model):
    __table_args__ = (
        db.UniqueConstraint("command_id", "name", name="unique_param_name_per_command"),
    )
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)
    valtype = db.Column(db.String(10))
    command_id = db.Column(db.Integer, db.ForeignKey("command.id"))

    def __repr__(self):
        return f"<Param {self.name}({self.valtype})>"
