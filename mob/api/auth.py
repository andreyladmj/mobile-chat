from os import urandom

from flask import request
from passlib.handlers.sha2_crypt import sha256_crypt

from mob.models import User, Token, Phone
from mob.utils import token_required, fail_response, success_response, auth_by_phone_required
from app import app, db


@app.route('/api/login', methods=['POST'])
def login():
    auth = request.form.to_dict()

    if not auth or not auth['id'] or not auth['password']:
        return fail_response({'message': 'Could not verify'}, 401)

    user = User.query.filter_by(id=auth['id']).first()

    if not user:
        return fail_response({'message': 'Could not verify'}, 401)

    if user.verify(auth['password']):
        token = Token(token=sha256_crypt.hash(str(urandom(64))), user_id=user.id)
        db.session.add(token)
        db.session.commit()
        user = user.to_dict()
        user['token'] = token.token
        return success_response(user)

    return fail_response({'message': 'Could not verify'}, 401)


@app.route('/api/validate_phone', methods=['POST'])
@auth_by_phone_required
def validate_phone(current_user):
    data = request.form.to_dict()
    pin = '1234'

    try:
        phone = Phone.query.filter(Phone.number==data['number']).filter(Phone.is_active==False)\
            .filter(Phone.user_id == current_user.id).first()

        if phone is not None and data['pin'] != pin:
            return fail_response({'message': 'Wrong pin'}, 401)

        phone.is_active = True
        db.session.commit()
        return success_response()

    except:
        pass

    return fail_response({'message': 'Number is wrong'}, 401)
