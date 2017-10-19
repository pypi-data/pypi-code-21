import datetime
from flask_jwt import jwt_required, current_identity
from flask_restplus import Resource, reqparse
from vidjon_messenger_api.models.message import MessageModel

class Message(Resource):

    @jwt_required()
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('start', type=int, location='args', help="This field has to be of value int.")
        parser.add_argument('stop', type=int, location='args', help="This field has to be of value int.")
        data = parser.parse_args()
        if data['start'] and data['stop']:
            messages = MessageModel.get_messages_for_user(current_identity.username, data['start']-1, data['stop'])
        else:
            messages = MessageModel.get_messages_for_user(current_identity.username)
        return {'messages': list(map(lambda x: x.json(), messages))}

    @jwt_required()
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('to_user',
                            type=str,
                            required=True,
                            help="This field has to be a string, the username of the user receiving the message."
                            )
        parser.add_argument('content',
                            type=str,
                            required=True,
                            help="This field has to be a string, this is the content of the message."
                            )
        data = parser.parse_args()
        message = MessageModel(current_identity.username, data['to_user'],data['content'], datetime.datetime.now())
        try:
            message.add_to_db()
            MessageModel.persist_to_database()
        except BaseException as err:
            return {"message": "An error occurred sending the message. {}".format(err)}, 500
        return message.json(), 201

    @jwt_required()
    def delete(self):
        parser = reqparse.RequestParser()
        parser.add_argument('ids', type=int, required = True, action='append', help = "The ids to delete have to be a list of integers")
        ids_to_delete = parser.parse_args()['ids']
        messages_in_database = MessageModel.get_messages_by_list(ids_to_delete)
        results = []
        for _id in ids_to_delete:
            message_in_database = next((x for x in messages_in_database if x.id == _id), None)
            if message_in_database:
                message_in_database.mark_as_delete()
                results.append({"id": _id, "Message": "Message deleted from the database"})
            else:
                results.append({"id": _id, "Message": "Message was not in database"})
        try:
            MessageModel.persist_to_database()
        except BaseException as err:
            return {"message": "An error occurred deleting messages. {}".format(err)}, 500
        return {"results": results}




