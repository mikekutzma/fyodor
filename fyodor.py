from app import app, db, login
from app.models import User, Service, Command, Param


@app.shell_context_processor
def make_shell_context():
    return {
        "db": db,
        "User": User,
        "Service": Service,
        "Command": Command,
        "Param": Param,
    }
