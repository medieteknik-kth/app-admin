from flask import Flask, render_template, request, redirect, jsonify, url_for, session, abort
from flask_dance.contrib.google import make_google_blueprint, google
from flask_dance.consumer import oauth_authorized
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func, text
import requests
import os
import uuid

from datetime import datetime, date
import ics
import arrow

from exponent_server_sdk import PushClient
from exponent_server_sdk import PushMessage

import locale
locale.setlocale(locale.LC_ALL, 'sv_SE.UTF-8')

committees = [
    {
        "name": "Styrelsen",
        "logo": "/static/images/styrelsen.png"
    },
    {
        "name": "MKM",
        "logo": "/static/images/mkm.png"
    },
    {
        "name": "Kommunikationsnämnden",
        "logo": "/static/images/komn.png"
    },
    {
        "name": "Näringslivsgruppen",
        "logo": "/static/images/nlg.png"
    },
    {
        "name": "Idrottsnämnden",
        "logo": "/static/images/idrott.png"
    },
    {
        "name": "Matlaget",
        "logo": "/static/images/matlaget.png"
    },
    {
        "name": "Medielabbet",
        "logo": "/static/images/medielabbet.png"
    },
    {
        "name": "Spexmästeriet",
        "logo": "/static/images/spex.png"
    },
    {
        "name": "Studienämnden",
        "logo": "/static/images/sn.png"
    },
    {
        "name": "Spelnörderiet",
        "logo": "/static/images/medieteknik.png"
    },
    {
        "name": "METAdorerna",
        "logo": "/static/images/metadorerna.png"
    },
    {
        "name": "Mottagningen",
        "logo": "/static/images/mtgn.png"
    },
    {
        "name": "Sånglederiet",
        "logo": "/static/images/sanglederiet.png"
    },
    {
        "name": "Valberedningen",
        "logo": "/static/images/valberedningen.png"
    },
    {
        "name": "Qulturnämnden",
        "logo": "/static/images/qn.png"
    },
    {
        "name": "METAspexet"
    },
    {
        "name": "Fotogruppen"
    },
    {
        "name": "Sektionen för Medieteknik",
        "logo": "/static/images/medieteknik.png"
    },
    {
        "name": "Datasektionen"
    },
    {
        "name": "THS"
    }
]

app = Flask(__name__)
app.config.from_pyfile('flask.cfg')
db = SQLAlchemy(app)

class Event(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String(256))
    committee = db.Column(db.String(256))
    location = db.Column(db.String(256))
    start = db.Column(db.DateTime())
    end = db.Column(db.DateTime())
    description = db.Column(db.Text())
    cover_image = db.Column(db.String(256))
    facebook_url = db.Column(db.String(256))
    published = db.Column(db.Boolean())

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "committee": self.committee,
            "location": self.location,
            "start": str(arrow.get(self.start).replace(tzinfo="Europe/Stockholm")),
            "end": str(arrow.get(self.end).replace(tzinfo="Europe/Stockholm")),
            "description": self.description,
            "cover_image": self.cover_image,
            "published": self.published,
            "facebook_url": self.facebook_url
        }

class NotificationSubscription(db.Model):
    token = db.Column(db.String(512), primary_key=True)
    active = db.Column(db.Boolean())

    styrelsen = db.Column(db.Boolean())
    mkm = db.Column(db.Boolean())
    komn = db.Column(db.Boolean())
    nlg = db.Column(db.Boolean())
    idrott = db.Column(db.Boolean())
    matlaget = db.Column(db.Boolean())
    medielabbet = db.Column(db.Boolean())
    spex = db.Column(db.Boolean())
    sn = db.Column(db.Boolean())
    spel = db.Column(db.Boolean())
    metadorerna = db.Column(db.Boolean())
    mtgn = db.Column(db.Boolean())
    sanglederiet = db.Column(db.Boolean())
    valberedningen = db.Column(db.Boolean())
    qn = db.Column(db.Boolean())
    metaspexet = db.Column(db.Boolean())
    fotogruppen = db.Column(db.Boolean())
    data = db.Column(db.Boolean())
    ths = db.Column(db.Boolean())

google_bp = make_google_blueprint(
    client_id=app.config["GOOGLE_CLIENT_ID"],
    client_secret=app.config["GOOGLE_CLIENT_SECRET"],
    scope=[
        "https://www.googleapis.com/auth/plus.me",
        "https://www.googleapis.com/auth/userinfo.email",
    ],
    hosted_domain="medieteknik.com"
)
app.register_blueprint(google_bp, url_prefix="/login")

def send_notification_to_subscriptions(committee, body, data):
    committee_code = ""
    if committee == "Styrelsen":
        committee_code = "styrelsen"
    elif committee == "MKM":
        committee_code = "mkm"
    elif committee == "Kommunikationsnämnden":
        committee_code = "komn"

    messages = []
    for subscription in NotificationSubscription.query.filter(NotificationSubscription.active.is_(True),text(committee_code + "=:trueValue")).params(trueValue=True).all():
        messages.append(PushMessage(to=subscription.token, body=body, data=data))

    responses = PushClient().publish_multiple(messages)

    for response in responses:
        if response.status != "ok":
            print(response.message)

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

@app.template_filter('format_datetime')
def format_datetime(value, format="%Y-%m-%d %H:%M"):
    if value is None:
        return ""
    return value.strftime(format)

@app.template_filter("in_future")
def in_future(dt):
    return datetime.now() < dt

@app.route("/logout")
def logout():
    del google_bp.token
    session.clear()
    return redirect(url_for("google.login"))

@app.route("/privacypolicy")
def privacypolicy():
    return render_template("privacypolicy.html")

@app.route("/")
def list_events():
    if not google.authorized:
        return redirect(url_for("google.login"))
    events = Event.query.all()
    return render_template("list.html", events=events)

@app.route("/notifications")
def list_notifications():
    if not google.authorized:
        return redirect(url_for("google.login"))
    subscriptions = NotificationSubscription.query.all()
    return render_template("subscriptions.html", subscriptions=subscriptions)

@app.route("/settings")
def settings():
    if not google.authorized:
        return redirect(url_for("google.login"))
    return render_template("settings.html")

@app.route("/edit/<id>")
def edit_event(id):
    if not google.authorized:
        return redirect(url_for("google.login"))
    event = Event.query.get(id)
    if event == None:
        return "Kunde inte hitta event."
    else:
        return render_template("edit.html", event=event, committees=committees)

@app.route("/delete/<id>")
def delete_event(id):
    if not google.authorized:
        return redirect(url_for("google.login"))
    db.session.delete(Event.query.get(id))
    db.session.commit()
    return redirect("/")

@app.route("/new")
def new_event():
    if not google.authorized:
        return redirect(url_for("google.login"))
    return render_template("new.html", committees=committees)

@app.route("/submit", methods=["POST"])
def submit_event():
    if not google.authorized:
        return redirect(url_for("google.login"))

    event = Event()
    event.title = request.form["title"]
    event.committee = request.form["committee"]
    event.location = request.form["location"]
    event.description = request.form["description"]
    event.start = datetime.strptime(request.form["start"], "%Y-%m-%d %H:%M")
    event.end = datetime.strptime(request.form["end"], "%Y-%m-%d %H:%M")
    event.published = (True if request.form.get("published") == "on" else False)
    event.cover_image = ""
    event.facebook_url = request.form["facebook_url"]

    if "cover_image" in request.files:
        cover_image = request.files['cover_image']
        if cover_image:
            original_filename, file_extension = os.path.splitext(cover_image.filename)
            filename = str(uuid.uuid4()) + file_extension
            cover_image.save(os.path.join("static/uploads/", filename))
            event.cover_image = request.url_root + "static/uploads/" + filename

    db.session.add(event)
    db.session.commit()

    send_notification_to_subscriptions(event.committee, "Nytt event från " + event.committee + ": " + event.title, {"id": event.id, "title": event.title})

    return redirect("/")

@app.route("/update", methods=["POST"])
def update_event():
    if not google.authorized:
        return redirect(url_for("google.login"))

    event = Event.query.get(request.form["id"])
    event.title = request.form["title"]
    event.committee = request.form["committee"]
    event.location = request.form["location"]
    event.description = request.form["description"]
    event.start = datetime.strptime(request.form["start"], "%Y-%m-%d %H:%M")
    event.end = datetime.strptime(request.form["end"], "%Y-%m-%d %H:%M")
    event.published = (True if request.form.get("published") == "on" else False)
    event.facebook_url = request.form["facebook_url"]

    if "cover_image" in request.files:
        cover_image = request.files['cover_image']
        if cover_image:
            original_filename, file_extension = os.path.splitext(cover_image.filename)
            filename = str(uuid.uuid4()) + file_extension
            cover_image.save(os.path.join("static/uploads/", filename))
            event.cover_image = request.url_root + "static/uploads/" + filename
    else:
        event.cover_image = request.form["cover_image_filename"]

    db.session.commit()

    return redirect("/")

@app.route("/remove_old_events")
def remove_old_events():
    if not google.authorized:
        return redirect(url_for("google.login"))
    # TODO
    return redirect("/")

@app.route("/remove_old_images")
def remove_old_images():
    if not google.authorized:
        return redirect(url_for("google.login"))
    # TODO
    return redirect("/")

@app.route("/test_notification")
def test_notis():
    messages = []
    for subscription in NotificationSubscription.query.filter(NotificationSubscription.active.is_(True)).all():
        messages.append(PushMessage(to=subscription.token, body="Här är en notis!", data={"id": 1, "title": "SM#1"}))

    responses = PushClient().publish_multiple(messages)

    message = ""

    for response in responses:
        message += response.status + ": " + response.message +"<br>"

    return "Notiser:<br>" + message

@app.route("/api/committee")
def api_committe_list():
    return jsonify(committees)

@app.route("/api/event")
def api_event_list():
    if request.args.get("format") == "app-v1":
        obj = {}

        # Fel i tidszoner?
        events = Event.query.filter(Event.published.is_(True), Event.end > datetime.now()).order_by(Event.start).all()

        return jsonify([i.to_dict() for i in events])
    elif "id" in request.args:
        event = Event.query.filter_by(id=request.args.get("id")).first_or_404()
        return jsonify(event.to_dict())
    elif request.args.get("format") == "ical":
        c = ics.Calendar()
        c.creator = "Sektionen för Medieteknik"

        for event in Event.query.filter(Event.published.is_(True)).all():
            e = ics.Event(name=event.title, begin=arrow.get(event.start).replace(tzinfo="Europe/Stockholm"), end=arrow.get(event.end).replace(tzinfo="Europe/Stockholm"), location=event.location)
            c.events.add(e)

        return str(c)
    elif "format" not in request.args:
        return jsonify([i.to_dict() for i in Event.query.filter_by(published=True).all()])

    return "Invalid format."

@app.route("/api/register_notification", methods=["POST"])
def api_register_notifications():
    obj = request.get_json()

    if obj is None or "token" not in obj:
        return "Invalid format."

    subscription = NotificationSubscription.query.get(obj["token"])
    if subscription == None:
        subscription = NotificationSubscription(token=obj["token"], active=True)
        db.session.add(subscription)

    if "styrelsen" in obj:
        subscription.styrelsen = obj["styrelsen"]
    if "mkm" in obj:
        subscription.mkm = obj["mkm"]
    if "komn" in obj:
        subscription.komn = obj["komn"]
    if "nlg" in obj:
        subscription.nlg = obj["nlg"]
    if "idrott" in obj:
        subscription.idrott = obj["idrott"]
    if "matlaget" in obj:
        subscription.matlaget = obj["matlaget"]
    if "medielabbet" in obj:
        subscription.medielabbet = obj["medielabbet"]
    if "spex" in obj:
        subscription.spex = obj["spex"]
    if "sn" in obj:
        subscription.sn = obj["sn"]
    if "spel" in obj:
        subscription.spel = obj["spel"]
    if "metadorerna" in obj:
        subscription.metadorerna = obj["metadorerna"]
    if "mtgn" in obj:
        subscription.mtgn = obj["mtgn"]
    if "sanglederiet" in obj:
        subscription.sanglederiet = obj["sanglederiet"]
    if "valberedningen" in obj:
        subscription.valberedningen = obj["valberedningen"]
    if "qn" in obj:
        subscription.qn = obj["qn"]
    if "metaspexet" in obj:
        subscription.metaspexet = obj["metaspexet"]
    if "fotogruppen" in obj:
        subscription.fotogruppen = obj["fotogruppen"]
    if "data" in obj:
        subscription.data = obj["data"]
    if "ths" in obj:
        subscription.ths = obj["ths"]

    db.session.commit()
    return "Saved notification settings."
