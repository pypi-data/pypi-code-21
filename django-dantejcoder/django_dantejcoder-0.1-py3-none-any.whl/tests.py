import json
from django.test import TestCase
from .coder import DanteJcoder
from .models import CityTest, RegionTest, EmptyModel, StandardModel, TypeModel
from django.contrib.auth.models import User


class TestDanteEncoder(TestCase):
    def setUp(self):
        self.region = RegionTest.objects.create(name='Perm edge')
        self.city1 = CityTest.objects.create(name='Perm', region=self.region)
        self.city2 = CityTest.objects.create(name='Zaton', region=self.region)
        self.standard = StandardModel.objects.create()
        self.tmodel = TypeModel.objects.create()
        self.user = User.objects.create_user('test', 'test@test.com', 'test123456')

    def test_standart_object(self):
        obj = [1, 2, 3]
        self.assertJSONEqual(json.dumps(obj, cls=DanteJcoder), '[1, 2, 3]')

    def test_one_model(self):
        self.assertJSONEqual(json.dumps(self.region, cls=DanteJcoder), '{"name": "Perm edge"}')

    def test_related_model(self):
        self.assertJSONEqual(json.dumps(self.city1, cls=DanteJcoder),
                             '{"name": "Perm", "test": true, "region": {"name": "Perm edge"}}')

    def test_queryset(self):
        regions = RegionTest.objects.all()
        self.assertJSONEqual(json.dumps(regions, cls=DanteJcoder), '[{"name": "Perm edge"}]')
        # пустой
        empty_queriset = EmptyModel.objects.all()
        self.assertJSONEqual(json.dumps(empty_queriset, cls=DanteJcoder), '[]')

    def test_without_to_json(self):
        self.assertJSONEqual(json.dumps(self.standard, cls=DanteJcoder), '{"id": 1, "name": "Standard", "val": 1}')

    def test_get_field_names(self):
        self.assertEqual([field.name for field in StandardModel._meta.fields], ['id', 'name', 'val'])

    def test_get_field_values(self):
        standard = self.standard
        values = [getattr(standard, field.name) for field in StandardModel._meta.fields]
        self.assertEqual(values, [1, 'Standard', 1])

    def test_field_types(self):
        start = self.tmodel
        end = json.dumps(start, cls=DanteJcoder)
        result = '{"id": 1, "mbool": false, "mdate": "2017-11-25", "mdatetime": "2017-11-25 09:41:06", "mtime": "09:52:07"}'
        self.assertJSONEqual(end, result)

    def test_user_to_json(self):
        end_json = json.dumps(self.user, cls=DanteJcoder)
        end = json.loads(end_json)
        self.assertTrue('date_joined' in end)
        self.assertEqual(end['email'], 'test@test.com')
        self.assertEqual(end['first_name'], '')
        self.assertEqual(end['id'], 1)
        self.assertTrue(end['is_active'])
        self.assertFalse(end['is_staff'])
        self.assertFalse(end['is_superuser'])
        self.assertIsNone(end['last_login'])
        self.assertEqual(end['last_name'], '')
        self.assertTrue('password' in end)
        self.assertEqual(end['username'], 'test')
