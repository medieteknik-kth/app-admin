from app.shared.models import db
import arrow

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
