from flask import request
from flask_restful import Resource

from mob.models import Phone, Contact, Message
from mob.utils import success_response, fail_response, auth_by_phone_required
from app import db


class MessagesResource(Resource):
    @auth_by_phone_required
    def post(self, number, current_user):
        data = request.form.to_dict()
        message = data['message']

        phone = Phone.query.filter(Phone.number == number).first()

        if phone is None:
            return fail_response({'message': 'Undefined number'}, 404)

        contact = Contact.query.filter(Contact.user_id == current_user.id). \
            filter(Contact.recipient_id == phone.user_id).first()

        if contact is None:
            return fail_response({'message': 'Undefined contact'}, 404)

        if contact.recipient_id == current_user.id:
            return fail_response({'message': 'You can\'t send message to yourself'}, 403)

        message = Message(recipient_id=contact.recipient_id, message=message, user_id=current_user.id)
        db.session.add(message)
        db.session.commit()

        return success_response(message.to_dict())

    @auth_by_phone_required
    def get(self, number, current_user):
        data = request.form.to_dict()
        last_id = data.get('last_id', 0)
        limit = data.get('limit', 10)

        phone = Phone.query.filter(Phone.number == number).first()

        if phone is None:
            return fail_response({'message': 'Undefined number'}, 404)

        db_messages = Message.query.filter(Message.id > last_id)\
            .filter(Message.recipient_id == phone.user_id)\
            .filter(Message.user_id == current_user.id) \
            .order_by(Message.created_at) \
            .limit(limit)\
            .all()

        messages = []

        for message in db_messages:
            messages.append(message.to_dict())

        return success_response(messages)
