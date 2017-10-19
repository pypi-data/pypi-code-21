from flask import Flask
from flask_jwt import JWT
from flask_restplus import Api
from vidjon_messenger_api.security import authenticate, identity
from vidjon_messenger_api.resources.message import Message
from vidjon_messenger_api.resources.user import UserRegister
from vidjon_messenger_api.db import db

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'vidjon'
api = Api(app, version='2.0', title="Messenger API", description="A simple API to send and retrieve messages for users.")
jwt = JWT(app, authenticate, identity)  # /auth
api.add_resource(Message, '/message')
api.add_resource(UserRegister, '/register')

@app.before_first_request
def create_table():
    db.create_all()

def main():
    db.init_app(app)
    app.run(port=5000, debug=True)

if __name__ == '__main__':
    main()





