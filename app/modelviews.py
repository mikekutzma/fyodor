from flask_admin import AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user


class AdminModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin


class AdminIndexViewLock(AdminIndexView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin
