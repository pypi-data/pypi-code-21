from vidjon_messenger_api.db import db

class MessageModel(db.Model):
    __tablename__ = 'messages'

    id = db.Column(db.Integer, primary_key=True)
    from_user = db.Column(db.String(80))
    to_user = db.Column(db.String(80))
    content = db.Column(db.String())
    date = db.Column(db.DateTime())
    is_read = db.Column(db.Boolean,default=False)

    def __init__(self, from_user, to_user, content, date):
        self.from_user = from_user
        self.to_user = to_user
        self.content = content
        self.date = date

    def json(self):
        return {"id": str(self.id), 'date': self.date.strftime("%Y-%m-%d %H:%M:%S"),"from": self.from_user,"to:": self.to_user, "content": self.content, "is_read": str(self.is_read)}

    def add_to_db(self):
        db.session.add(self)

    def mark_as_read(self):
        self.is_read = True

    def mark_as_delete(self):
        db.session.delete(self)

    @classmethod
    def persist_to_database(cls):
        db.session.commit()

    @classmethod
    def get_messages_for_user(cls, username, start=None, stop=None):
        m_query = cls.query.filter_by(to_user=username).order_by(MessageModel.date)

        if start is not None and stop is not None:
            m_query = m_query.slice(start, stop)
        else:
            m_query = m_query.filter_by(is_read=False)

        messages = m_query.all()
        for message in messages: message.mark_as_read()
        cls.persist_to_database()
        return messages

    @classmethod
    def get_messages_by_list(cls, ids):
        return cls.query.filter(MessageModel.id.in_(ids)).all()
