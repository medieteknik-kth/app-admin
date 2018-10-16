from flask import render_template, redirect, url_for
from flask_dance.contrib.google import google
from . import settings_bp

import subprocess

@settings_bp.route("/")
def index():
    if not google.authorized:
        return redirect(url_for("google.login"))
    return render_template("settings.html")

@settings_bp.route("/deploy")
def git():
    if not google.authorized:
        return redirect(url_for("google.login"))
    process1 = subprocess.run(["git", "pull"], stdout=subprocess.PIPE)
    process2 = subprocess.run(["systemctl", "restart", "mediaappadmin"], stdout=subprocess.PIPE)
    message = process1.stdout
    return render_template("message.html", title="Deploy Info", message=message)
