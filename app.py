from os import urandom

from flask import Flask, Blueprint, jsonify, make_response
from flask_restful import Api

from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = urandom(32)
api_bp = Blueprint('api', __name__, url_prefix='/api')
app.config.from_pyfile('config.cfg')
api = Api(api_bp)
db = SQLAlchemy(app)

import commands

from mob.api.users import UserResource, UsersResource
from mob.api.contacts import ContactResource, ContactsResource
from mob.api.messages import MessagesResource
from mob.api.auth import *

api.add_resource(UserResource, '/users/<string:number>')
api.add_resource(UsersResource, '/users')

api.add_resource(ContactResource, '/contacts/<string:number>')
api.add_resource(ContactsResource, '/contacts')

api.add_resource(MessagesResource, '/messages/<string:number>')
app.register_blueprint(api_bp)


if __name__ == '__main__':
    app.run(debug=True)
