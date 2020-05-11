from functools import wraps

import datetime
from flask import request, make_response, jsonify
from passlib.handlers.sha2_crypt import sha256_crypt
from sqlalchemy.orm.collections import InstrumentedList
from werkzeug.security import check_password_hash
from mob.exceptions import ApiException

from sqlalchemy.dialects import postgresql
from app import app
from mob.models import Token, Phone


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']

        if not token:
            return fail_response({'message': 'Token is missing!'}, 401)

        try:
            delta = datetime.datetime.now() - datetime.timedelta(seconds=30)
            db_token = Token.query.filter(Token.token == token).filter(Token.created_at >= delta).first()
            current_user = db_token.user
        except:
            return fail_response({'message': 'Token is invalid!'}, 401)

        kwargs['current_user'] = current_user

        return f(*args, **kwargs)

    return decorated


def auth_by_phone_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'x-access-phone' not in request.headers:
            return fail_response({'message': 'Phone number is required!'}, 401)

        if 'x-access-pin' not in request.headers:
            return fail_response({'message': 'PIN is required!'}, 401)

        number = request.headers['x-access-phone']
        pin = request.headers['x-access-pin']

        phone = Phone.query.filter(Phone.number == number).first()

        if phone is None:
            return fail_response({'message': 'Number was not found!'}, 404)

        if pin != '1234':
            return fail_response({'message': 'PIN is wrong!'}, 404)

        kwargs['current_user'] = phone.user

        return f(*args, **kwargs)

    return decorated


def to_dict(object):
    if type(object) is list or type(object) is InstrumentedList:
        new_list = []

        for item in object:
            new_list.append(to_dict(item))

        return new_list

    dict = object.to_dict()

    for k, v in dict.items():
        if type(v) is InstrumentedList:
            dict[k] = to_dict(v)

    return dict


def print_sql(model):
    return model.statement.compile(dialect=postgresql.dialect())


def success_response(data={}, status_code=200):
    return make_response(jsonify({
        'success': 1,
        'errors': [],
        'result': data
    }), status_code)


def fail_response(data={}, status_code=400):
    return make_response(jsonify({
        'success': 0,
        'errors': data,
        'result': []
    }), status_code)


@app.errorhandler(ApiException)
def handle_api_error(error):
    return make_response(jsonify(error.to_dict()), error.status_code)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'message': str(error)}), 404)