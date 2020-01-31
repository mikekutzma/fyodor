from flask import Flask
from flask_admin import Admin
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from config import Config

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

login = LoginManager(app)
login.login_view = "login"


from app import routes, models, modelviews

admin = Admin(
    app, index_view=modelviews.AdminIndexViewLock(), template_mode="bootstrap3"
)
admin.add_view(modelviews.AdminModelView(models.User, db.session))
