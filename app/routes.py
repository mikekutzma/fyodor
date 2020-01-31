import requests

from flask import render_template, request, redirect, url_for, flash
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse

from app import app, db
from app.forms import LoginForm, get_param_form, RPCForm, UserRegistrationForm
from app.models import Service, User


@app.route("/", methods=["GET", "POST"])
@app.route("/home", methods=["GET", "POST"])
@app.route("/rpc", methods=["GET", "POST"])
@login_required
def home():

    params = Service.query.first().commands.first().params.all()
    RPCForm.params = get_param_form(params)
    form = RPCForm()

    if form.validate_on_submit():
        app.logger.error(form.data)
        make_request(
            form.service.data,
            form.command.data,
            {k: v for k, v in form.params.data.items() if k != "csrf_token"},
        )
        flash(f"Call submitted to {form.service.data} for {form.command.data}")
        return redirect(url_for("home"))

    return render_template("rpc.html", form=form)


@app.route("/apirpc", methods=["GET", "POST"])
@login_required
def api_rpc():

    data = request.get_json(force=True)
    app.logger.error(data)
    make_request(
        data.get("service"),
        data.get("command"),
        {k: v for k, v in data.get("params", {}).items()},
    )
    return "OK"


@app.route("/login", methods=["GET", "POST"])
def login():

    app.logger.info("login called")
    if current_user.is_authenticated:
        app.logger.info("%s already authenticated", current_user)
        return redirect(url_for("home"))

    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        app.logger.info("Valid submission for %s", user)

        # See if junk entry or wrong password
        if user is None or not user.check_password(form.password.data):
            flash("Invalid username or password")
            app.logger.info("Invalid login")
            return redirect(url_for("login"))

        # See if user is not yet approved
        if not user.is_approved:
            flash("User not yet approved")
            return redirect(url_for("login"))

        # Thus login was valid
        login_user(user, remember=form.remember_me.data)

        next_page = request.args.get("next")
        if not next_page or url_parse(next_page).netloc != "":
            next_page = url_for("home")
        return redirect(next_page)

    return render_template("login.html", form=form)


@app.route("/test", methods=["POST", "GET"])
@login_required
def test():
    return "Yeap"


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("home"))


@app.route("/registeruser", methods=["GET", "POST"])
def registeruser():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    form = UserRegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("Registration successful. Account approval pending.")
        return redirect(url_for("login"))
    return render_template("register.html", title="Register", form=form)


def make_request(service, command, params={}):
    s = Service.query.filter_by(name=service).first()
    c = s.commands.filter_by(name=command).first()
    p_dict = {c.params.filter_by(name=k).first(): v for k, v in params.items()}
    payload = {p.name: eval(p.valtype)(k) for p, k in p_dict.items()}
    url = f"http://{s.ip}/{c.target}"
    app.logger.error("Making RPC to url %s with payload %s", url, payload)
    r = requests.get(url, params=payload)
    return r
