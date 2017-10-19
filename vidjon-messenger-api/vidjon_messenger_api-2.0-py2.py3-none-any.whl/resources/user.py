from flask_restplus import Resource, reqparse
from vidjon_messenger_api.models.user import UserModel

class UserRegister(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('username',
                        type=str,
                        required=True,
                        help="This field cannot be left blank!"
                        )
    parser.add_argument('password',
                        type=str,
                        required=True,
                        help="This field cannot be left blank!"
                        )

    def post(self):
        data = UserRegister.parser.parse_args()

        if UserModel.find_by_username(data['username']):
            return {"message": "A user with that username already exists"}, 400

        user = UserModel(**data)
        try:
            user.save_to_db()
        except BaseException as err:
            return {"message": "An error occurred when creating the user. {}".format(err)}, 500

        return {"message": "User created successfully."}, 201


