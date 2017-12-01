from django.core.urlresolvers import reverse
from shuup_testutils.cases import ApiAuthAdminTestCase

from attrim.testutils.generators import ModelsGen


class ClsTest(ApiAuthAdminTestCase):
    @classmethod
    def set_up_class(cls):
        super().set_up_class()
        cls.cls_create_url = reverse('shuup_admin:attrim.new')

    def set_up(self):
        super().set_up()
        self.gen = ModelsGen()

    def test_get(self):
        cls = self.gen.attrim.cls()
        response = self.client.get(
            path=reverse('shuup_admin:attrim.edit', kwargs={'pk': cls.pk}),
        )
        self.assert_equal(response.status_code, 200)
        self.assert_contains(response, 'clsPrimaryKey: {},'.format(cls.pk))
        self.assert_contains(response, 'isEditForm: true,')

    def test_create(self):
        response = self.client.get(reverse('shuup_admin:attrim.new'))
        self.assert_equal(response.status_code, 200)
        self.assert_contains(response, 'isEditForm: false,')
