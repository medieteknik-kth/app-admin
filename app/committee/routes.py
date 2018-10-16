from flask import render_template, redirect, url_for, request
from . import committee_bp
from flask_dance.contrib.google import google

from app.committee.models import Committee
from app.notifications.models import NotificationSubscription
from app.shared.models import db

from app.notifications.notifications import get_committee_code
from sqlalchemy import text, desc

@committee_bp.route("/")
def index():
    if not google.authorized:
        return redirect(url_for("google.login"))
    committees = Committee.query.order_by(desc(Committee.weight)).all()

    subDict = {}

    for committee in committees:
        committee_code = get_committee_code(committee.name)
        if committee_code != "":
            count = NotificationSubscription.query.filter(text("active=1 AND " + committee_code + "=1")).count()
            subDict[committee.name] = count
        else:
            subDict[committee.name] = "Går ej att prenumerera på"

    return render_template("committee_list.html", committees=committees, subDict=subDict)

@committee_bp.route("/new")
def new():
    if not google.authorized:
        return redirect(url_for("google.login"))
    return render_template("committee_new.html")

@committee_bp.route("/edit/<id>")
def edit(id):
    if not google.authorized:
        return redirect(url_for("google.login"))
    committee = Committee.query.get(id)
    if committee == None:
        return "Kunde inte hitta nämnd."
    else:
        return render_template("committee_edit.html", committee=committee)

@committee_bp.route("/delete/<id>")
def delete(id):
    if not google.authorized:
        return redirect(url_for("google.login"))
    db.session.delete(Committee.query.get(id))
    db.session.commit()
    return redirect(url_for("committee.index"))

@committee_bp.route("/submit", methods=["POST"])
def submit():
    if not google.authorized:
        return redirect(url_for("google.login"))
    committee = Committee()
    committee.name = request.form["name"]
    committee.shortDescription = request.form["shortDescription"]
    committee.description = request.form["description"]
    committee.weight = request.form["weight"]

    db.session.add(committee)
    db.session.commit()

    return redirect(url_for("committee.index"))

@committee_bp.route("/update", methods=["POST"])
def update():
    if not google.authorized:
        return redirect(url_for("google.login"))
    committee = Committee.query.get(request.form["id"])
    committee.name = request.form["name"]
    committee.shortDescription = request.form["shortDescription"]
    committee.description = request.form["description"]
    committee.weight = request.form["weight"]

    db.session.commit()

    return redirect(url_for("committee.index"))
