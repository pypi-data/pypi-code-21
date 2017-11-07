# # -*- coding:utf-8 -*-
# from django.test import TestCase
# 
# from fe_core.models import User, Entity
# from tests.factories import UserFactory, EntityFactory, ApplicationFactory
# 
# 
# class TestUsuario(TestCase):
#     def setUp(self):
#         self.email = 'meu_email@domainname.com'
#         self.password = 'minha-senha-secreta'
#         self.entidade = EntityFactory()
#         self.produto = ProductFactory()
#         self.aplicacao = ApplicationFactory()
# 
#     def test_contructor(self):
#         usuario = User.objects.create()
#         self.assertIsNotNone(usuario)
#         self.assertFalse(usuario.is_staff)
#         self.assertFalse(usuario.is_superuser)
#         self.assertTrue(usuario.is_active)
# 
#     def test_check_password(self):
#         usuario = UserFactory(password=self.password)
#         self.assertTrue(usuario.check_password(self.password))
# 
#     def test_create_user(self):
#         usuario = User.objects.create_auth_user(
#             email=self.email,
#             password=self.password
#         )
#         self.assertIsNotNone(usuario)
#         self.assertFalse(usuario.is_staff)
#         self.assertFalse(usuario.is_superuser)
#         self.assertTrue(usuario.is_active)
# 
#     def test_create_user_com_entidade(self):
#         self.assertEquals(2, Entity.objects.all().count())
#         usuario = User.objects.create_auth_user(
#             email=self.email,
#             password=self.password,
#             entity=self.entidade
#         )
#         self.assertEquals(self.entidade, usuario.entity)
#         self.assertEquals(2, Entity.objects.all().count())
# 
#     def test_create_user_sem_entidade(self):
#         self.assertEquals(2, Entity.objects.all().count())
#         usuario = User.objects.create_auth_user(
#             email=self.email,
#             password=self.password
#         )
#         self.assertIsNotNone(usuario.entity)
#         self.assertEquals(3, Entity.objects.all().count())
# 
#     def test_create_user_sem_entidade_com_produto(self):
#         self.assertEquals(2, Entity.objects.all().count())
#         usuario = User.objects.create_auth_user(
#             email=self.email,
#             password=self.password,
#             product=self.produto
#         )
#         self.assertIsNotNone(usuario.entity)
#         self.assertEquals(3, Entity.objects.all().count())
#         self.assertEquals(self.produto, usuario.entity.product_set.get(uuid=self.produto.uuid))
# 
# 
# class TestUsuarioAplicacao(TestCase):
#     def __validate_aplicacao(self, aplicacao, usuario):
#         self.assertIsNotNone(aplicacao.client_id)
#         self.assertIsNotNone(aplicacao.user, usuario)
#         self.assertEquals('', aplicacao.redirect_uris)
#         self.assertEquals(Application.CLIENT_PUBLIC, aplicacao.client_type)
#         self.assertEquals(Application.GRANT_PASSWORD, aplicacao.authorization_grant_type)
#         self.assertIsNotNone(aplicacao.client_secret)
#         self.assertEquals(usuario.email, aplicacao.name)
#         self.assertFalse(aplicacao.skip_authorization)
# 
#     def setUp(self):
#         self.email = 'meu_email@domainname.com'
#         self.password = 'minha-senha-secreta'
#         self.entidade = EntityFactory()
#         self.produto = ProductFactory()
#         self.aplicacao = ApplicationFactory()
# 
#     def test_get_or_create_aplicacao_quando_aplicacao_nao_existe(self):
#         usuario = UserFactory()
#         self.assertEquals(1, Application.objects.all().count())
#         aplicacao = usuario.get_or_create_application()
#         self.assertIsNotNone(aplicacao)
#         self.assertEquals(2, Application.objects.all().count())
#         self.assertNotEquals(aplicacao, self.aplicacao)
#         usuario.refresh_from_db()
#         self.assertIsNotNone(usuario)
#         self.__validate_aplicacao(aplicacao, usuario)
# 
#     def test_get_or_create_aplicacao_quando_aplicacao_ja_existe(self):
#         usuario = UserFactory()
#         self.aplicacao.user = usuario
#         self.aplicacao.name = usuario.email
#         self.aplicacao.save()
#         self.assertEquals(1, Application.objects.all().count())
#         aplicacao = usuario.get_or_create_application()
#         self.assertIsNotNone(aplicacao)
#         self.assertEquals(1, Application.objects.all().count())
#         self.assertEquals(aplicacao, self.aplicacao)
#         usuario.refresh_from_db()
#         self.assertIsNotNone(usuario)
#         self.__validate_aplicacao(aplicacao, usuario)
# 
#     def test_get_or_create_aplicacao_quando_existem_varias_aplicaoes_para_mesmo_usuario(self):
#         usuario = UserFactory()
#         ApplicationFactory(user=usuario)
#         ApplicationFactory(user=usuario)
#         ApplicationFactory(user=usuario)
#         self.assertEquals(4, Application.objects.all().count())
#         aplicacao = usuario.get_or_create_application()
#         self.assertIsNotNone(aplicacao)
#         self.assertEquals(2, Application.objects.all().count())
#         self.assertNotEquals(aplicacao, self.aplicacao)
#         usuario.refresh_from_db()
#         self.assertIsNotNone(usuario)
#         self.__validate_aplicacao(aplicacao, usuario)
