from .base import BaseData, OptionalDict


class MessageCreateData(BaseData):
    def __init__(self, title=None, content=None, skip_type=None, skip_target=None,
                 content_clickable=None, send_nick_name=None, type=None,
                 target_user_id=None, send_at=None):
        self.data = OptionalDict()
        self.data['title'] = title
        self.data['content'] = content
        self.data['skip_type'] = skip_type
        self.data['skip_target'] = skip_target
        self.data['content_clickable'] = content_clickable
        self.data['send_nick_name'] = send_nick_name
        self.data['type'] = type
        self.data['target_user_id'] = target_user_id
        self.data['send_at'] = send_at
