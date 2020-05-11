from wtforms import Form, StringField, PasswordField, validators

from flask import request
from flask_restful import Resource

from mob.models import Phone, User
from mob.utils import success_response, fail_response, auth_by_phone_required, to_dict
from mob.validators import Unique, LengthIfExists, PhoneValidator
from app import db


class RegistrationForm(Form):
    first_name = StringField('First name', [validators.DataRequired(), validators.Length(min=2, max=128)])
    last_name = StringField('Last name', [validators.DataRequired(), validators.Length(min=2, max=128)])
    phone = StringField('Phone', [
        validators.DataRequired(),
        PhoneValidator(),
        Unique(
            Phone,
            Phone.number,
            message='This phone number already exists'),
        validators.Length(min=10, max=10)
    ])
    ### maybe will be require in future
    # password = PasswordField('New Password', [
    #     validators.DataRequired(),
    #     validators.Length(min=6),
    #     validators.EqualTo('confirm', message='Passwords must match')
    # ])
    # confirm = PasswordField('Repeat Password')


class UsersResource(Resource):
    def post(self):
        data = request.form.to_dict()
        form = RegistrationForm(request.form)

        if not form.validate():
            return fail_response(dict(form.errors.items()), 500)

        user = User(first_name=data['first_name'],
                    last_name=data['last_name'])
        db.session.add(user)
        db.session.commit()

        phone = Phone(number=data['phone'], user_id=user.id)
        db.session.add(phone)
        db.session.commit()

        user = user.to_dict()
        user['phones'] = [phone.to_dict()]
        return success_response(user)

    def get(self):
        users = User.query.filter(User.phones.any()).all()
        return success_response(to_dict(users))


class UpdateProfileForm(Form):
    first_name = StringField('First name', [LengthIfExists(min=2, max=128)])
    last_name = StringField('Last name', [LengthIfExists(min=2, max=128)])
    password = PasswordField('New Password', [LengthIfExists(min=6)])


class UserResource(Resource):
    @auth_by_phone_required
    def delete(self, number, current_user):
        if not current_user.has_number(number):
            return fail_response({'message': 'Forbidden'}, 403)

        Phone.query.filter(Phone.user_id == current_user.id).delete()
        User.query.filter(User.id == current_user.id).delete()
        db.session.commit()
        return success_response()

    @auth_by_phone_required
    def post(self, number, current_user):
        if not current_user.has_number(number):
            return fail_response({'message': 'Forbidden'}, 403)

        data = request.form.to_dict()
        form = UpdateProfileForm(request.form)

        if not form.validate():
            return fail_response(dict(form.errors.items()), 500)

        user = User.query.filter(User.id == current_user.id).first()

        for item in data:
            setattr(user, item, data[item])

        db.session.commit()
        return success_response(to_dict(user))

    def get(self, number):
        phone = Phone.query.filter(Phone.number == number).first()

        if phone is None:
            return fail_response({'user': 'Not found'}, 404)

        return success_response(to_dict(phone.user))
