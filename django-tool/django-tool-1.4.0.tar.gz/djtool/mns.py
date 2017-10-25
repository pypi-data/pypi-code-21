
from mns.account import Account
from mns.topic import DirectSMSInfo
from mns.topic import TopicMessage
from django.conf import settings


class MNS:
    def __init__(self):
        c = ['MNS_ENDPOINT', 'MNS_ACCESSID', 'MNS_ACCESSKEY', 'MNS_TOPIC']
        for one in c:
            if not hasattr(settings, one):
                raise Exception('请配置%s参数' % one)
            else:
                setattr(self, one, getattr(settings, one))
        self.account = Account(self.MNS_ENDPOINT, self.MNS_ACCESSID, self.MNS_ACCESSKEY)
        self.topic = self.account.get_topic(self.MNS_TOPIC)

    def sms(self, sign_name, template_code, single=False):
        self.sms = DirectSMSInfo(free_sign_name=sign_name, template_code=template_code, single=single)
        return True

    def send(self, receiver, params):
        self.sms.add_receiver(receiver=receiver, params=params)
        msg = TopicMessage('mm', direct_sms=self.sms)
        return self.topic.publish_message(msg)


mns = MNS()
