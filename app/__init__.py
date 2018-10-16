import locale
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from app.home import home_bp
import app.home.routes

from app.settings import settings_bp
import app.settings.routes

from app.event import event_bp
import app.event.routes

from app.committee import committee_bp
import app.committee.routes

from app.api import api_bp
import app.api.routes

from app.shared.models import db

from flask_dance.contrib.google import make_google_blueprint, google
from flask_dance.consumer import oauth_authorized

locale.setlocale(locale.LC_ALL, 'sv_SE.UTF-8')
app = Flask(__name__)
app.config.from_pyfile("flask.cfg")
db.init_app(app)

auth_bp = make_google_blueprint(
    client_id=app.config["GOOGLE_CLIENT_ID"],
    client_secret=app.config["GOOGLE_CLIENT_SECRET"],
    scope=[
        "https://www.googleapis.com/auth/plus.me",
        "https://www.googleapis.com/auth/userinfo.email",
    ],
    hosted_domain="medieteknik.com"
)

@oauth_authorized.connect
def logged_in(blueprint, token):
    resp_json = google.get("/oauth2/v2/userinfo").json()
    if resp_json["hd"] != blueprint.authorization_url_params["hd"]:
        requests.post(
            "https://accounts.google.com/o/oauth2/revoke",
            params={"token": token["access_token"]}
        )
        session.clear()
        abort(403)

app.register_blueprint(auth_bp, url_prefix="/login")
app.register_blueprint(home_bp)
app.register_blueprint(event_bp, url_prefix='/event')
app.register_blueprint(committee_bp, url_prefix='/committee')
app.register_blueprint(api_bp, url_prefix='/api')
app.register_blueprint(settings_bp, url_prefix='/settings')
