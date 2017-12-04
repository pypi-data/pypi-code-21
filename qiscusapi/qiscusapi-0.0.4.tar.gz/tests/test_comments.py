import unittest
from qiscusapi.api import Api


class TestPostComments(unittest.TestCase):

    maxDiff = None

    def test_post_comment_text_success(self):
        api = Api('nchat-djc1dquyoc7rwk6', 'ddbb2dc955f85798290a8590c9583c0a')
        r = api.post_comment_text(
            'coba@aja.com', '45743', 'hello qiscus'
        )
        self.assertEqual(
            r.comment_message,
            'hello qiscus'
        )

    def test_post_comment_text_fail(self):
        api = Api('nchat-djc1dquyoc7rwk6', 'ddbb2dc955f85798290a8590c9583c0a')
        r = api.post_comment_text(
            '', '', 'test unittesting'
        )
        self.assertEqual(
            (r.error_message, r.error_status_code),
            ('Validation error', 400)
        )

    def test_post_comment_buttons_success(self):
        api = Api('nchat-djc1dquyoc7rwk6', 'ddbb2dc955f85798290a8590c9583c0a')
        r = api.post_comment_buttons(
            'coba@aja.com',
            '45743',
            '{"text":"silahkan pencet","buttons":[{"label":"button1","type":"postback","payload":{'
            '"url":"http://somewhere.com/button1","method":"get","payload":null}},{"label":"button2","type":"link",'
            '"payload":{"url":"http://somewhere.com/button2?id=123","method":"get","payload":null}}]} '
        )
        self.assertEqual(
            (r.comment_payload_buttons[0].buttons_label, r.comment_payload_buttons[0].buttons_type),
            ('button1', 'postback')
        )

    def test_post_comment_buttons_fail(self):
        api = Api('nchat-djc1dquyoc7rwk6', 'ddbb2dc955f85798290a8590c9583c0a')
        r = api.post_comment_buttons(
            'coba@aja.com',
            '45743',
            ''
        )
        self.assertEqual(
            (r.error_message, r.error_status_code),
            ('Validation error', 400)
        )

    def test_post_comment_card_success(self):
        api = Api('nchat-djc1dquyoc7rwk6', 'ddbb2dc955f85798290a8590c9583c0a')
        r = api.post_comment_card(
            'coba@aja.com',
            '45743',
            '{"text":"Special deal buat sista nih..","image":"http://url.com/gambar.jpg","title":"Atasan Blouse Tunik '
            'Wanita Baju Muslim Worie Longtop","description":"Oleh sippnshop\n96% (666 feedback)\nRp 49.000.00,'
            '-\nBUY 2 GET 1 FREE!!!","url":"http://url.com/baju?id=123&track_from_chat_room=123","buttons":[{'
            '"label":"button1","type":"postback","payload":{"url":"http://somewhere.com/button1","method":"get",'
            '"payload":null}},{"label":"button2","type":"link","payload":{'
            '"url":"http://somewhere.com/button2?id=123","method":"get","payload":null}}]} '
        )
        self.assertEqual(
            r.comment_message,
            'Special deal buat sista nih..'
        )

    def test_post_comment_card_fail(self):
        api = Api('nchat-djc1dquyoc7rwk6', 'ddbb2dc955f85798290a8590c9583c0a')
        r = api.post_comment_card(
            'coba@aja.com',
            '45743',
            ''
        )
        self.assertEqual(
            (r.error_message, r.error_status_code),
            ('Validation error', 400)
        )

    def test_post_comment_account_linking_succes(self):
        api = Api('nchat-djc1dquyoc7rwk6', 'ddbb2dc955f85798290a8590c9583c0a')
        r = api.post_comment_account_linking(
            'coba@aja.com',
            '45743',
            '{"text":"silahkan login","url":"http://google.com","redirect_url":"http://google.com/redirect",'
            '"params":{"user_id":1,"topic_id":1,"button_text":"ini button","view_title":"title",'
            '"success_message":"sip!"}} '
        )
        self.assertEqual(
            r.payload_text,
            'silahkan login'
        )

    def test_post_comment_account_linking_fail(self):
        api = Api('nchat-djc1dquyoc7rwk6', 'ddbb2dc955f85798290a8590c9583c0a')
        r = api.post_comment_account_linking(
            'coba@aja.com',
            '45743',
            ''
        )
        self.assertEqual(
            (r.error_message, r.error_status_code),
            ('Validation error', 400)
        )

    def test_post_comment_custom_succes(self):
        api = Api('nchat-djc1dquyoc7rwk6', 'ddbb2dc955f85798290a8590c9583c0a')
        r = api.post_comment_account_linking(
            'coba@aja.com',
            '45743',
            '{"text":"silahkan login","url":"http://google.com","redirect_url":"http://google.com/redirect",'
            '"params":{"user_id":1,"topic_id":1,"button_text":"ini button","view_title":"title",'
            '"success_message":"sip!"}} '
        )
        self.assertEqual(
            r.payload_text,
            'silahkan login'
        )

    def test_post_comment_custom_fail(self):
        api = Api('nchat-djc1dquyoc7rwk6', 'ddbb2dc955f85798290a8590c9583c0a')
        r = api.post_comment_account_linking(
            'coba@aja.com',
            '45743',
            ''
        )
        self.assertEqual(
            (r.error_message, r.error_status_code),
            ('Validation error', 400)
        )

    def test_post_comment_postback_button_success(self):
        api = Api('nchat-djc1dquyoc7rwk6', 'ddbb2dc955f85798290a8590c9583c0a')
        r = api.post_comment_postback_button(
            'coba@aja.com',
            '45743',
            '{"url":"http://telkomnews.bots.qiscus.com/v1/postback","method":"post","payload":{"intent":"POPULER_NEWS"}}'
        )
        self.assertEqual(
            r.payload_url,
            'http://telkomnews.bots.qiscus.com/v1/postback'
        )

    def test_post_comment_postback_button_fail(self):
        api = Api('nchat-djc1dquyoc7rwk6', 'ddbb2dc955f85798290a8590c9583c0a')
        r = api.post_comment_postback_button(
            '',
            '',
            '{"url":"http://telkomnews.bots.qiscus.com/v1/postback","method":"post","payload":{"intent":"POPULER_NEWS"}}'
        )
        self.assertEqual(
            (r.error_message, r.error_status_code),
            ('Validation error', 400)
        )
