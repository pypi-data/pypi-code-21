def test_fixture(postgresql_instance):
	assert hasattr(postgresql_instance, 'port')
