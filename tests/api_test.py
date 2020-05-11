import random

from faker import Faker
from flask import json
from flask_testing import TestCase

from app import db, app
from mob.models import User, Phone, Token, Message


class ApiTest(TestCase):
    phone = None
    pin = None

    def create_app(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite://"
        app.config['TESTING'] = True
        return app

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def get_users(self):
        response = self.client.get('/api/users', follow_redirects=True)
        return json.loads(response.data), response.status_code

    def get_user(self, number):
        response = self.client.get('/api/users/{}'.format(number), follow_redirects=True)
        return json.loads(response.data), response.status_code

    def login(self, id, password):
        response = self.client.post('/api/login', data=dict(
            id=id,
            password=password,
        ), follow_redirects=True)

        return json.loads(response.data), response.status_code

    def create_user(self, first_name, last_name, phone):
        response = self.client.post('/api/users', data=dict(
            first_name=first_name,
            last_name=last_name,
            phone=phone,
        ), follow_redirects=True)

        return json.loads(response.data), response.status_code

    def update_user(self, phone, first_name, last_name):
        response = self.client.post('/api/users/{}'.format(phone), data=dict(
            first_name=first_name,
            last_name=last_name,
        ), headers=self.get_headers(),
           follow_redirects=True)

        return json.loads(response.data), response.status_code

    def delete_user(self, number):
        response = self.client.delete('/api/users/{}'.format(number), headers=self.get_headers(),
                                      follow_redirects=True)

        return json.loads(response.data), response.status_code

    def validate_phone(self, pin, number):
        response = self.client.post('/api/validate_phone', data=dict(
            pin=pin,
            number=number,
        ), headers=self.get_headers(),
           follow_redirects=True)

        return json.loads(response.data), response.status_code

    def create_batch_users(self, n=50):
        for i in range(n):
            number = random.randrange(1000000000,9999999999)
            user = self.create_random_user(str(number))
            yield user, number

    def create_random_user(self, number, valid=True):
        fake = Faker()
        user = User(first_name=fake.first_name(), last_name=fake.last_name())
        db.session.add(user)
        db.session.commit()

        phone = Phone(number=number, user_id=user.id, is_active=valid)

        db.session.add(phone)
        db.session.commit()

        return user

    def login_by_user(self, user=None, number='0509998877', pin='1234'):
        if user is None:
            user = self.create_random_user(number=number)

        self.set_phone(number, pin)
        return user

    def get_headers(self):
        headers = {}

        if self.phone is not None:
            headers['x-access-phone'] = self.phone

        if self.pin is not None:
            headers['x-access-pin'] = self.pin

        return headers

    def set_phone(self, phone, pin='1234'):
        self.phone = phone
        self.pin = pin

    def add_contact(self, number):
        response = self.client.post('/api/contacts', data=dict(number=number),
                                    headers=self.get_headers(), follow_redirects=True)
        return json.loads(response.data), response.status_code

    def add_batch_messages(self, owner_id=None, n=50):
        fake = Faker()
        number = '0509998870'
        user = self.create_random_user(number)
        for i in range(n):
            message = Message(recipient_id=user.id, message=fake.sentence(), user_id=owner_id)
            db.session.add(message)
        db.session.commit()
        return user, number