from app.notifications.models import NotificationSubscription

from exponent_server_sdk import PushClient
from exponent_server_sdk import PushMessage

from sqlalchemy import text

def get_committee_code(committee):
    committee_code = ""
    if committee == "Styrelsen":
        committee_code = "styrelsen"
    elif committee == "MKM":
        committee_code = "mkm"
    elif committee == "Idrottsnämnden":
        committee_code = "idrott"
    elif committee == "Näringslivsgruppen":
        committee_code = "nlg"
    elif committee == "Kommunikationsnämnden":
        committee_code = "komn"
    elif committee == "Fotogruppen":
        committee_code = "fotogruppen"
    elif committee == "Matlaget":
        committee_code = "matlaget"
    elif committee == "Medielabbet":
        committee_code = "medielabbet"
    elif committee == "METAdorerna":
        committee_code = "metadorerna"
    elif committee == "Mottagningen":
        committee_code = "mtgn"
    elif committee == "Qulturnämnden":
        committee_code = "qn"
    elif committee == "Sånglederiet":
        committee_code = "sanglederiet"
    elif committee == "Studienämnden":
        committee_code = "sn"
    elif committee == "Spexmästeriet":
        committee_code = "spex"
    elif committee == "Valberedningen":
        committee_code = "valberedningen"
    elif committee == "METAspexet":
        committee_code = "metaspexet"
    elif committee == "Spelnörderiet":
        committee_code = "spel"
    elif committee == "Medias Branschdag":
        committee_code = "mbd"
    elif committee == "Datasektionen":
        committee_code = "data"
    elif committee == "THS":
        committee_code = "ths"
    return committee_code

def send_notification_to_subscriptions(committee, body, data):
    committee_code = get_committee_code(committee)
    if committee_code == "":
        return

    messages = []
    for subscription in NotificationSubscription.query.filter(text("active=1 AND " + committee_code + "=1")).all():
        messages.append(PushMessage(to=subscription.token, body=body, data=data))

    responses = PushClient().publish_multiple(messages)

    for response in responses:
        if response.status != "ok":
            print(response.message)
