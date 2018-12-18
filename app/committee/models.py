from app.shared.models import db

class Committee(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(256))
    shortDescription = db.Column(db.String(256))
    description = db.Column(db.Text())
    weight = db.Column(db.Integer())

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "shortDescription": self.shortDescription,
            "description": self.description,
            "weight": self.weight
        }
