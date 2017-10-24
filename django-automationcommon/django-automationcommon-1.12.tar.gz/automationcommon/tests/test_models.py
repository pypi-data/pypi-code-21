import datetime
import logging

from django.contrib.auth.models import User, AnonymousUser
from testfixtures import LogCapture

from automationcommon.models import set_local_user, Audit, ModelChangeMixin, clear_local_user, LOCAL_USER_WARNING
from automationcommon.tests.utils import UnitTestCase


class FakeModel:
    pk = 1

    def save(self, *args, **kwargs):
        pass

    def delete(self, *args, **kwargs):
        pass


class TestModel(ModelChangeMixin, FakeModel):

    def __init__(self, *args, **kwargs):
        self.fields = {
            'name': 'the round window',
            'description': "it's round",
        }
        super(TestModel, self).__init__(*args, **kwargs)

    @property
    def _dict(self):
        return self.fields.copy()


class ModelsTests(UnitTestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username="it123")

    def setUp(self):
        set_local_user(self.user)
        self.test_model = TestModel()

    def test_audit_no_user(self):

        clear_local_user()

        with LogCapture(level=logging.INFO) as log_capture:

            # test
            self.test_model.fields.update({'description': "it's a round window"})
            self.test_model.save()

            # check
            self.assertEqual(0, Audit.objects.count())
            log_capture.check((
                'automationcommon', 'WARNING',
                "Don't know who made this change: (model=TestModel:1, field=description, "
                "old='it's round', new='it's a round window')"
            ), (
                'automationcommon', 'WARNING', LOCAL_USER_WARNING
            ))

    def test_audit_single_change(self):

        start = datetime.datetime.now()

        # test
        self.test_model.fields.update({'description': "it's a round window"})
        self.test_model.save()

        # check
        self.assertEqual(1, Audit.objects.count())
        audit = Audit.objects.all().first()
        self.assertLessEqual(start, audit.when)
        self.assertEqual(self.user, audit.who)
        self.assertEqual('TestModel', audit.model)
        self.assertEqual(1, audit.model_pk)
        self.assertEqual('description', audit.field)
        self.assertEqual("it's round", audit.old)
        self.assertEqual("it's a round window", audit.new)

    def test_audit_anonymous_user(self):

        set_local_user(AnonymousUser())

        # test
        self.test_model.fields.update({'description': "it's a round window"})
        self.test_model.save()

        # check
        self.assertEqual(1, Audit.objects.count())
        self.assertIsNone(Audit.objects.all().first().who)

    def test_audit_multiple_change(self):

        # test
        self.test_model.fields = {
            'name': 'the square window',
            'description': "no wait, it's actually square!",
        }
        self.test_model.save()

        # check
        self.assertEqual(2, Audit.objects.count())
        audits = Audit.objects.all().order_by('field')
        self.assertEqual('description', audits[0].field)
        self.assertEqual("it's round", audits[0].old)
        self.assertEqual("no wait, it's actually square!", audits[0].new)
        self.assertEqual('name', audits[1].field)
        self.assertEqual("the round window", audits[1].old)
        self.assertEqual("the square window", audits[1].new)

    def test_audit_delete(self):

        # test
        self.test_model.delete()

        # check
        self.assertEqual(2, Audit.objects.count())
        audits = Audit.objects.all().order_by('field')
        self.assertEqual('description', audits[0].field)
        self.assertEqual("it's round", audits[0].old)
        self.assertIsNone(audits[0].new)
        self.assertEqual('name', audits[1].field)
        self.assertEqual("the round window", audits[1].old)
        self.assertIsNone(audits[1].new)

    def tearDown(self):
        clear_local_user()
