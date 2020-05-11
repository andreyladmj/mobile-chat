from sqlalchemy.orm import joinedload

from flask import request
from flask_restful import Resource

from mob.models import Phone, Contact
from mob.utils import success_response, fail_response, auth_by_phone_required, to_dict
from app import db


class ContactsResource(Resource):
    @auth_by_phone_required
    def post(self, current_user):
        data = request.form.to_dict()
        number = data['number']

        phone = Phone.query.filter(Phone.is_active==True).filter(Phone.number==number).first()

        if phone is None:
            return fail_response({'message': 'Undefined number'}, 404)

        if phone.user_id == current_user.id:
            return fail_response({'message': 'You can\'t add yourself'}, 403)

        contact = Contact(recipient_id=phone.user_id, user_id=current_user.id)
        db.session.add(contact)
        db.session.commit()

        return success_response(contact.to_dict())

    @auth_by_phone_required
    def get(self, current_user):
        data = request.form.to_dict()
        last_id = data.get('last_id', 0)
        limit = data.get('limit', 10)
        contacts = Contact.query.filter(Contact.id > last_id).filter(Contact.user_id == current_user.id)\
            .limit(limit).options(joinedload('user')).all()

        return success_response(to_dict(contacts))


class ContactResource(Resource):
    @auth_by_phone_required
    def delete(self, number, current_user):
        if not current_user.has_contact(number):
            return fail_response({'message': 'Forbidden'}, 403)

        phone = Phone.query.filter(Phone.number == number).first()

        Contact.query.filter(Contact.user_id == current_user.id).\
            filter(Contact.recipient_id == phone.user_id).delete()

        db.session.commit()
        return success_response()
