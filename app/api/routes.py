from flask import jsonify, request
from . import api_bp

from app.committee.models import Committee
from app.event.models import Event
from app.notifications.models import NotificationSubscription
from app.shared.models import db

from datetime import datetime
from sqlalchemy import desc

@api_bp.route("/committee")
def committe():
    if "id" in request.args:
        committee = Committee.query.filter_by(id=request.args.get("id")).first_or_404()
        return jsonify(committee.to_dict())
    else:
        committees = Committee.query.order_by(desc(Committee.weight)).all()
        return jsonify([i.to_dict() for i in committees])

@api_bp.route("/event")
def event():
    if request.args.get("format") == "app-v1":
        obj = {}

        # Fel i tidszoner?
        events = Event.query.filter(Event.published.is_(True), Event.end > datetime.now()).order_by(Event.current.desc(), Event.start).all()

        return jsonify([i.to_dict() for i in events])
    elif "id" in request.args:
        event = Event.query.filter_by(id=request.args.get("id")).first_or_404()
        return jsonify(event.to_dict())
    elif "committee" in request.args:
        events = Event.query.filter(Event.published.is_(True), Event.end > datetime.now(), Event.committee == request.args.get("committee")).all()
        return jsonify([i.to_dict() for i in events])
    elif request.args.get("format") == "ical":
        c = ics.Calendar()
        c.creator = "Sektionen för Medieteknik"

        for event in Event.query.filter(Event.published.is_(True)).all():
            e = ics.Event(name=event.title, begin=arrow.get(event.start).replace(tzinfo="Europe/Stockholm"), end=arrow.get(event.end).replace(tzinfo="Europe/Stockholm"), location=event.location)
            c.events.add(e)

        return str(c)
    elif "format" not in request.args:
        return jsonify([i.to_dict() for i in Event.query.filter_by(published=True).all()])

@api_bp.route("/register_notification", methods=["POST"])
def register_notifications():
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
    if "mbd" in obj:
        subscription.mbd = obj["mbd"]
    if "data" in obj:
        subscription.data = obj["data"]
    if "ths" in obj:
        subscription.ths = obj["ths"]

    db.session.commit()
    return "Saved notification settings."
