from flask import render_template, redirect, url_for
from flask_dance.contrib.google import google
from . import settings_bp

import os

@settings_bp.route("/")
def index():
    #if not google.authorized:
        #return redirect(url_for("google.login"))
    return render_template("settings.html")
