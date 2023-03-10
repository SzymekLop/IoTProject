from . import db
from abc import abstractmethod
from sqlalchemy.sql import func


class Employee(db.Model):
    card_id = db.Column(db.String(20), primary_key=True, autoincrement=True)
    name = db.Column(db.String(100))

    def __str__(self):
        return "Employee: %s id: %s" % (self.name, self.card_id)


class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    card_id = db.Column(db.String(20), db.ForeignKey('employee.card_id'))
    time = db.Column(db.String(40))

    def __str__(self):
        return "Log_%d card id: %s at time: %16s" % (self.id, self.card_id, self.time)
