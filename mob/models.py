import datetime

from passlib.handlers.sha2_crypt import sha256_crypt
from sqlalchemy.orm import backref

from app import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String(128), nullable=False)
    last_name = db.Column(db.String(128), nullable=False)
    password = db.Column(db.String(77))

    def __eq__(self, other):
        return type(self) is type(other) and self.id == other.id

    def __repr__(self):
        return '<User %r>' % self.id

    def has_number(self, number):
        for phone in self.phones:
            if phone.number == number:
                return True

        return False

    def has_contact(self, number):
        for contact in self.contacts:
            if contact.recipient.has_number(number):
                return True

        return False

    def verify(self, password):
        if sha256_crypt.verify(password, self.password):
            return True

        return False

    @staticmethod
    def crypt_password(password):
        return sha256_crypt.hash(str(password))

    def to_dict(self):
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'phones': self.phones,
        }


class Phone(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    number = db.Column(db.String(128), unique=True, nullable=False)
    is_active = db.Column(db.Boolean, nullable=False, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='cascade', onupdate='cascade'))
    user = db.relationship("User", backref=backref('phones', uselist=True, cascade='delete, all'))

    dictable = ['id', 'number', 'is_active', 'user_id', 'user']

    def __repr__(self):
        return '<Phone %r>' % self.number

    def __eq__(self, other):
        return type(self) is type(other) and self.id == other.id

    def to_dict(self):
        return {
            'id': self.id,
            'number': self.number,
            'is_active': self.is_active,
        }


class Token(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    token = db.Column(db.String(77), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='cascade', onupdate='cascade'))
    user = db.relationship("User", backref="tokens")
    created_at = db.Column(db.DateTime, default=datetime.datetime.now)


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    message = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='cascade', onupdate='cascade'))
    user = db.relationship("User", backref="messages", foreign_keys=[user_id])
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='cascade', onupdate='cascade'))
    recipient = db.relationship("User", foreign_keys=[recipient_id])
    created_at = db.Column(db.DateTime, default=datetime.datetime.now)

    def to_dict(self):
        return {
            'id': self.id,
            'message': self.message,
            'user_id': self.user_id,
            'recipient_id': self.recipient_id,
            'created_at': self.created_at,
        }


class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='cascade', onupdate='cascade'))
    user = db.relationship("User", backref="contacts", foreign_keys=[user_id])
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='cascade', onupdate='cascade'))
    recipient = db.relationship("User", foreign_keys=[recipient_id])
    created_at = db.Column(db.DateTime, default=datetime.datetime.now)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'recipient_id': self.recipient_id,
            'created_at': self.created_at,
        }
