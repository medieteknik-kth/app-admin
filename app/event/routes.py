from flask import render_template, request, redirect, jsonify, url_for
from . import event_bp
from flask_dance.contrib.google import google

from app.event.models import Event
from app.committee.models import Committee

from app.shared.models import db

from app.notifications.notifications import send_notification_to_subscriptions

from datetime import datetime
import os
import uuid

@event_bp.app_template_filter("in_future")
def in_future(dt):
    return datetime.now() < dt

@event_bp.app_template_filter('format_datetime')
def format_datetime(value, format="%Y-%m-%d %H:%M"):
    if value is None:
        return ""
    return value.strftime(format)

@event_bp.route("/")
def index():
    if not google.authorized:
        return redirect(url_for("google.login"))
    events = Event.query.all()
    return render_template("event_list.html", events=events)

@event_bp.route("/edit/<id>")
def edit(id):
    if not google.authorized:
        return redirect(url_for("google.login"))
    event = Event.query.get(id)
    if event == None:
        return "Kunde inte hitta event."
    else:
        committees = Committee.query.all()
        return render_template("event_edit.html", event=event, committees=committees)

@event_bp.route("/delete/<id>")
def delete(id):
    if not google.authorized:
        return redirect(url_for("google.login"))
    db.session.delete(Event.query.get(id))
    db.session.commit()
    return redirect(url_for("event.index"))

@event_bp.route("/new")
def new():
    if not google.authorized:
        return redirect(url_for("google.login"))
    committees = Committee.query.all()
    return render_template("event_new.html", committees=committees)

@event_bp.route("/submit", methods=["POST"])
def submit():
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
    event.current = (True if request.form.get("current") == "on" else False)

    if "cover_image" in request.files:
        cover_image = request.files['cover_image']
        if cover_image:
            original_filename, file_extension = os.path.splitext(cover_image.filename)
            filename = str(uuid.uuid4()) + file_extension
            cover_image.save(os.path.join("app/static/uploads/", filename))
            event.cover_image = request.url_root + "static/uploads/" + filename

    db.session.add(event)
    db.session.commit()

    if event.published:
        send_notification_to_subscriptions(event.committee, "Nytt från " + event.committee + ": " + event.title, {"id": event.id, "title": event.title})

    return redirect(url_for("event.index"))

@event_bp.route("/update", methods=["POST"])
def update():
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
    event.current = (True if request.form.get("current") == "on" else False)
    event.facebook_url = request.form["facebook_url"]

    if "cover_image" in request.files:
        cover_image = request.files['cover_image']
        if cover_image:
            original_filename, file_extension = os.path.splitext(cover_image.filename)
            filename = str(uuid.uuid4()) + file_extension
            cover_image.save(os.path.join("app/static/uploads/", filename))
            event.cover_image = request.url_root + "static/uploads/" + filename
    else:
        event.cover_image = request.form["cover_image_filename"]

    db.session.commit()

    return redirect(url_for("event.index"))
