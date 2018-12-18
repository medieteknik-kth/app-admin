from flask import render_template, redirect, url_for
from flask_dance.contrib.google import google
from . import home_bp

@home_bp.route("/")
def index():
    if not google.authorized:
        return redirect(url_for("google.login"))
    return render_template("home.html")

@home_bp.route("/metatv/<id>")
def metatv(id):
    return render_template("metatv.html", video="/static/TV" + id + ".mp4")

@home_bp.route("/privacypolicy")
def privacypolicy():
    return render_template("privacypolicy.html")
