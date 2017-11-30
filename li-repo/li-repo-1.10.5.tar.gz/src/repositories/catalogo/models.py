# -*- coding: utf-8 -*-
from textwrap import dedent
from django.db.models import F, Q, Count, Sum, Max
from django.core.urlresolvers import reverse
from django.db import models, IntegrityError
from django.core.exceptions import ValidationError
from django.utils.text import slugify
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
from mptt.managers import TreeManager as _TreeManager
from mptt.models import MPTTModel, TreeForeignKey
from django.db.transaction import TransactionManagementError
from django.core.exceptions import MultipleObjectsReturned
from repositories.libs import utils
from repositories import custom_models
from unicodedata import normalize
import time
import random
import string
import logging
import operator
logger = logging.getLogger(__name__)


def remover_acentos(value):
    """Normalize the values."""
    try:
        return normalize('NFKD', value.decode('utf-8')).encode('ASCII', 'ignore')
    except UnicodeEncodeError:
        return normalize('NFKD', value).encode('ASCII', 'ignore')
    except Exception:
        return value


class ProdutoNaoPodeTerFilho(Exception):
    pass


class CategoriaManager(models.Manager):
    def alfabeticamente(self, conta_id, somente_ativas=True):
        categorias_sql = dedent(u'''\
            SELECT
              cat.categoria_id,cat.categoria_nome,cat.categoria_nome,cat.categoria_ativa,
              cat.categoria_posicao,cat.categoria_em_destaque,cat.categoria_descricao,
              cat.lft,cat.rght,cat.tree_id,cat.parent_id,cat.level,
              (CASE WHEN url.url_id IS NULL THEN CONCAT('/categoria/',cat.categoria_id,'.html') ELSE url.url_canonical_url END) AS categoria_url,
              cat.categoria_id_externo
            FROM catalogo.tb_categoria cat LEFT JOIN plataforma.tb_url url ON cat.categoria_id=url.categoria_id AND url.url_principal=TRUE
            WHERE cat.conta_id = %s %s
            ORDER BY cat.parent_id NULLS FIRST,
                     cat.categoria_posicao,
                     cat.categoria_nome''')
        categorias_sql = categorias_sql % \
                         ('%s', somente_ativas == True and \
                          u'AND cat.categoria_ativa = %s' or u'')
        formatting = somente_ativas == True and \
                     [conta_id, somente_ativas] or [conta_id]
        categorias = list(super(CategoriaManager, self).raw(
            categorias_sql, formatting))
        # Executa um prefetch para que todos os conteúdos já sejam
        # trazidos no cache por padrão.
        return categorias

    def agrupadas(self, conta_id, somente_ativas=True):
        categorias = self.alfabeticamente(conta_id, somente_ativas)
        categorias = utils.aninhar_categorias(categorias)
        return categorias

    def flat(self, conta_id, somente_ativas=True):
        categorias = self.agrupadas(conta_id, somente_ativas)
        categorias = utils.flat_categorias(categorias)
        return categorias


class TreeManager(_TreeManager):
    def rebuild_from_ground(self, **kwargs):
        """Erases all the mptt data and rebuild based on parent_id."""
        qs = self._mptt_filter(parent=None, **kwargs)
        qs.update(tree_id=None, lft=None, rght=None, level=None)
        self.partial_filtered_rebuild(**kwargs)

    def partial_filtered_rebuild(self, **kwargs):
        """Same as partial_rebuild but here you can passes the filtering arguments."""
        if not kwargs:
            return

        if self._base_manager:
            return self._base_manager.partial_custom_rebuild(**kwargs)
        opts = self.model._mptt_meta

        qs = self._mptt_filter(parent=None, **kwargs)
        if opts.order_insertion_by:
            qs = qs.order_by(*opts.order_insertion_by)
        pks = qs.values_list('pk', 'tree_id')

        if not pks:
            return

        for pk, tree_id in pks:
            self._rebuild_helper(pk, 1, tree_id)

    def _rebuild_helper(self, pk, left, tree_id, level=0):
        opts = self.model._mptt_meta
        right = left + 1

        qs = self._mptt_filter(parent__pk=pk)
        if opts.order_insertion_by:
            qs = qs.order_by(*opts.order_insertion_by)
        child_ids = qs.values_list('pk', flat=True)

        rebuild_helper = self._rebuild_helper

        if not tree_id:
            tree_id = self._get_next_tree_id()

        for child_id in child_ids:
            right = rebuild_helper(child_id, right, tree_id, level + 1)

        qs = self.model._default_manager.filter(pk=pk)
        self._mptt_update(qs,
                          left=left,
                          right=right,
                          level=level,
                          tree_id=tree_id
                          )

        return right + 1

    def insert_node(self, node, target, position='last-child', save=False, allow_existing_pk=False):
        """
        Sets up the tree state for ``node`` (which has not yet been
        inserted into in the database) so it will be positioned relative
        to a given ``target`` node as specified by ``position`` (when
        appropriate) it is inserted, with any neccessary space already
        having been made for it.

        A ``target`` of ``None`` indicates that ``node`` should be
        the last root node.

        If ``save`` is ``True``, ``node``'s ``save()`` method will be
        called before it is returned.

        NOTE: This is a low-level method; it does NOT respect ``MPTTMeta.order_insertion_by``.
        In most cases you should just set the node's parent and let mptt call this during save.
        """

        if self._base_manager:
            return self._base_manager.insert_node(node, target, position=position, save=save)

        if node.pk and not allow_existing_pk and self.filter(pk=node.pk).exists():
            raise ValueError('Cannot insert a node which has already been saved.')

        if (target is None) or (target.is_root_node() and position in ['left', 'right']):
            tree_id = self._get_next_tree_id()
            setattr(node, self.left_attr, 1)
            setattr(node, self.right_attr, 2)
            setattr(node, self.level_attr, 0)
            setattr(node, self.tree_id_attr, tree_id)
            setattr(node, self.parent_attr, None)
        else:
            setattr(node, self.left_attr, 0)
            setattr(node, self.level_attr, 0)

            space_target, level, left, parent, right_shift = \
                self._calculate_inter_tree_move_values(node, target, position)
            tree_id = getattr(parent, self.tree_id_attr)

            self._create_space(2, space_target, tree_id)

            setattr(node, self.left_attr, -left)
            setattr(node, self.right_attr, -left + 1)
            setattr(node, self.level_attr, -level)
            setattr(node, self.tree_id_attr, tree_id)
            setattr(node, self.parent_attr, parent)

            if parent:
                self._post_insert_update_cached_parent_right(parent, right_shift)

        if save:
            node.save()
        return node


class Categoria(MPTTModel):

    id = custom_models.BigAutoField(db_column="categoria_id", primary_key=True)
    id_externo = models.IntegerField(db_column="categoria_id_externo", null=True)
    data_criacao = models.DateTimeField(db_column="categoria_data_criacao", auto_now_add=True)
    data_modificacao = models.DateTimeField(db_column="categoria_data_modificacao", auto_now=True)
    ativa = models.BooleanField(db_column="categoria_ativa", default=True)
    posicao = models.IntegerField(db_column="categoria_posicao", default=0)
    destaque = models.BooleanField(db_column="categoria_em_destaque", default=False)
    url = models.CharField(db_column="categoria_url", null=True, max_length=255)

    nome = models.CharField(db_column='categoria_nome', max_length=255)
    descricao = models.TextField(db_column='categoria_descricao', null=True)

    conta = models.ForeignKey('plataforma.Conta', db_column="conta_id", related_name="categorias")
    contrato = models.ForeignKey('plataforma.Contrato', related_name="categorias")
    parent = TreeForeignKey("self", null=True, blank=True, related_name="children", on_delete=models.PROTECT)
    id_anymarket = models.IntegerField(db_column="categoria_id_anymarket", null=True, blank=True)

    ordenadas = CategoriaManager()
    objects = TreeManager()

    class MPTTMeta:
        order_insertion_by = ['posicao']
        master_tree = 'conta_id'

    class Meta:
        db_table = u"catalogo\".\"tb_categoria"
        verbose_name = u"Categoria"
        verbose_name_plural = u"Categorias"
        ordering = ["posicao"]
        get_latest_by = 'id'
        # unique_together = ("apelido", "conta")

    def __unicode__(self):
        return self.nome or unicode(self.id)

    def natural_key(self):
        return self.nome

    def save(self, *args, **kwargs):
        if isinstance(self.parent, basestring):
            self.parent_id = int(self.parent)
            delattr(self, 'parent')

        # Caso uma categoria seja definida como Inativa, todos os seus filhos
        # são definidos como inativo para que não haja problema no momento da
        # listagem das categorias na loja.
        if not self.ativa:
            self.get_descendants().update(ativa=False)

        if self.conta.id and not self.contrato_id:
            self.contrato_id = self.conta.contrato_id

        super(Categoria, self).save(*args, **kwargs)

    def ancestrais(self, *args, **kwargs):
        ancestors = super(Categoria, self).get_ancestors(*args, **kwargs)
        return ancestors.filter(conta_id=self.conta_id)

    @classmethod
    def reordenar_categorias(cls, categorias_ids):
        if not categorias_ids:
            return False

        categorias = Categoria.objects.filter(pk__in=categorias_ids)
        for categoria in categorias:
            try:
                posicao = categorias_ids.index(categoria.id)
            except ValueError:
                # Simplesmente ignora quando não consegue encontrar a posição.
                posicao = 0

            Categoria.objects.filter(pk=categoria.id).update(posicao=posicao)
        try:
            Categoria.objects.rebuild_from_ground(conta_id=categoria.conta_id)
        except Exception as e:
            msg = 'Erro ao tentar corrigir a arvore da conta %s. (ERRO: %s)' % (categoria.conta_id, e)
            logger.error(msg)

        return True

    @classmethod
    def mptt_partial_rebuild(cls, categoria):
        """Executa o partial_rebuild do MPTT e caso não consiga tentar
        corrigir o tree_id das categorias.

        Sempre que dá um erro ao fazer o rebuild é pq o tree_id está
        incorreto, quando isso acontece temos que redefinir os tree_ids
        e todas as variáveis do MPTT para que ele consiga refazer
        novamente o caminho das categorias.
        """
        try:
            Categoria.objects.partial_rebuild(categoria.tree_id)
            return
        except Exception as e:
            msg = 'Nao foi possivel fazer partial_rebuild, tentando usar ' \
                  '"Categoria.corrigir_tree_id()". (ERRO: %s)'
            logger.error(msg % e)

        try:
            Categoria.objects.rebuild_from_ground(conta_id=categoria.conta_id)
            return
        except Exception as e:
            msg = 'Erro ao tentar rebuild_from_ground. (ERRO: %s)'
            logger.error(msg % e)

        try:
            Categoria.corrigir_tree_id(categoria.conta)
            return
        except Exception as e:
            msg = 'Erro ao tentar corrigir o tree_id. (ERRO: %s)'
            logger.error(msg % e)

    @classmethod
    def corrigir_mptt(cls, conta):
        """Corrige as definições do MPTT para as categorias de uma conta."""
        with cls.objects.delay_mptt_updates():
            for cat in conta.categorias.all():
                cat.lft = cat.rght = cat.level = cat.tree_id = None
                cat.save()

    def get_absolute_url(self, usa_dominio=True):
        path = self.get_path()
        if usa_dominio:
            return u"http://{}/{}".format(self.conta.url_dominio, path.decode('utf-8'))
        return path

    def get_path(self):

        urls = self.urls.filter(principal=True)[:1]

        if urls is not None and urls.__len__() > 0 and urls[0]:
            url = urls[0]
        else:
            url = self.url

        if str(url)[:1] == '/':
            return str(url)[1:]
        else:
            return str(url)

    def adicionar_url(self, url):
        from repositories.plataforma.models import URL

        try:
            url_ = URL.objects.get(url=url, conta_id=self.conta_id)
        except URL.DoesNotExist:
            pass
        else:
            if url_.principal:
                raise IntegrityError
            else:
                url_.delete()
        url, primeira_url = URL.objects.get_or_create(url=url, categoria=self, conta=self.conta)
        return url

    def url_apelido(self):
        apelido = self.apelido
        return reverse('categoria_listar', kwargs={'apelido': apelido})

    def seo(self):
        from repositories.marketing.models import SEO

        if not hasattr(self, '_seo'):
            try:
                self._seo = SEO.objects.get(
                    tabela='tb_categoria', linha_id=self.id,
                    conta_id=self.conta_id)
            except SEO.DoesNotExist:
                return SEO.objects.create(
                    tabela='tb_categoria', linha_id=self.id,
                    conta_id=self.conta_id)
        return self._seo

    def atualizar_url(self, path_url):
        from repositories.plataforma.models import URL

        if not path_url:
            path_url = '/' + slugify(self.nome)

        def criar_url(path_url):

            # TODO: Isso aqui deve ficar a cargo do catalogo. Colocado um try para quebra galho e parar
            # de dar erro com frequencia.
            try:
                url, primeira_url = URL.objects.get_or_create(url=path_url, categoria=self, conta=self.conta)
            except TransactionManagementError:
                time.sleep(1)
                url, primeira_url = URL.objects.get_or_create(url=path_url, categoria=self, conta=self.conta)

            return url

        def adicionar_traco(s):
            try:
                s.index('.', -5, -1)
                tem_extensao = True
            except ValueError:
                tem_extensao = False

            if tem_extensao:
                l = s.split('.')
                l[-2] = u'%s-' % l[-2]
                s = u'.'.join(l)
            else:
                s = u'%s-' % s

            return s

        contagem = 0
        while True:
            contagem += 1

            # Caso a iteração seja maior que 10 retorna o erro para o lojista.
            if contagem >= 10:
                return False

            try:
                url_obj = criar_url(path_url)
            except IntegrityError as e:
                path_url = adicionar_traco(path_url)
                logger.debug('Erro ao criar URL para categoria. (ERRO: %s)' % e)
                continue
            else:
                url_obj.principal = True
                url_obj.save()

                URL.objects.filter(categoria=self) \
                    .exclude(pk=url_obj.id) \
                    .update(principal=False)
                break
        return True

    def separador_level(self, separador='-'):
        if self.level:
            return separador * self.level
        return ''

    def nome_provisorio(self):
        return 'categoria-rascunho-' + self.data_criacao.strftime('%Y-%m-%d-%H-%M-%S')


class Marca(models.Model):
    """Marca."""
    id = custom_models.BigAutoField(db_column='marca_id', primary_key=True)
    id_externo = models.IntegerField(db_column="marca_id_externo", null=True)
    data_criacao = models.DateTimeField(db_column='marca_data_criacao', auto_now_add=True)
    data_modificacao = models.DateTimeField(db_column='marca_data_modificacao', auto_now=True)
    ativo = models.BooleanField(db_column='marca_ativo', default=False)
    destaque = models.BooleanField(
        db_column="marca_destaque", default=False, null=False)
    imagem = models.CharField(
        db_column="marca_imagem_caminho", null=True, blank=True,
        max_length=256)
    nome = models.CharField(db_column='marca_nome', max_length=255, verbose_name='nome')
    apelido = models.CharField(db_column='marca_apelido', max_length=255, null=True)
    descricao = models.TextField(db_column='marca_descricao', null=True)

    conta = models.ForeignKey('plataforma.Conta', related_name='marcas', on_delete=models.CASCADE)
    contrato = models.ForeignKey('plataforma.Contrato', related_name="marcas")
    id_anymarket = models.IntegerField(db_column="marca_id_anymarket", null=True, blank=True)

    class Meta:
        db_table = u"catalogo\".\"tb_marca"
        verbose_name = u'Marca'
        verbose_name_plural = u'Marcas'
        ordering = ['id']
        get_latest_by = 'id'

    def __unicode__(self):
        return self.nome or unicode(self.id)

    def save(self, *args, **kwargs):
        if self.conta and not self.contrato_id:
            self.contrato_id = self.conta.contrato_id
        super(Marca, self).save(*args, **kwargs)

    def natural_key(self):
        return self.nome

    def get_absolute_url(self, usa_dominio=True):
        path = reverse('marca_listar', kwargs={'apelido': self.apelido})
        if usa_dominio:
            return u"http://{}/{}".format(self.conta.url_dominio, path)
        return path


class GradeMannager(models.Manager):
    def filtrar(self, conta_id):
        queryset = super(GradeMannager, self).get_queryset()
        # [2014-02-10 13:36] jonatasoliveira: Retirei o prefetech_related com produtos_grade pois ele estava
        # retornando todos os produtos relacionados as grades padrão do sistema.
        return queryset.filter(Q(conta_id=conta_id) | Q(conta_id__isnull=True))


class Grade(models.Model):
    """Grade para uma veriação de produtos."""
    id = custom_models.BigAutoField(db_column='grade_id', primary_key=True)
    id_externo = models.IntegerField(db_column='grade_id_externo', null=True, default=None)
    nome = models.CharField(db_column='grade_nome', max_length=255)
    nome_visivel = models.CharField(db_column='grade_nome_visivel', max_length=255)
    data_criacao = models.DateTimeField(db_column='grade_data_criacao', auto_now_add=True)
    data_modificacao = models.DateTimeField(db_column='grade_data_modificacao', auto_now=True, null=True)
    pode_ter_imagens = models.BooleanField(db_column="grade_pode_ter_imagens", null=False, default=False)
    tipo = models.CharField(db_column="grade_tipo", default="normal", max_length=32, null=False)
    # Ordenação das grades, sempre tem que ser maior que as grades do sistema.
    posicao = models.IntegerField(db_column="grade_posicao", null=None, default=1000)

    conta = models.ForeignKey('plataforma.Conta', related_name='grades', on_delete=models.CASCADE, null=True)
    contrato = models.ForeignKey('plataforma.Contrato', related_name="grades")

    _produtos = models.ManyToManyField('catalogo.Produto', through='catalogo.ProdutoGrade', related_name='_grades')
    id_anymarket = models.IntegerField(db_column="grade_id_anymarket", null=True, blank=True)

    objects = GradeMannager()

    class Meta:
        db_table = u"catalogo\".\"tb_grade"
        verbose_name = u'Grade'
        verbose_name_plural = u'Grades'
        ordering = ['posicao', 'nome']
        unique_together = (("conta", "nome"),)

    def __unicode__(self):
        return self.nome

    def save(self, *args, **kwargs):
        if self.conta and not self.contrato_id:
            self.contrato_id = self.conta.contrato_id
        super(Grade, self).save(*args, **kwargs)

    def criar_variacao(self, nome):
        variacao, criado = GradeVariacao.objects.get_or_create(
            nome=nome, grade=self, conta=self.conta)
        return variacao

    def selecionar_variacao(self, nome):
        """
        Retorna variação da grade
        """
        try:
            return self.variacoes.get(nome=nome)
        except MultipleObjectsReturned:
            return self.variacoes.filter(nome=nome)[0]
        except GradeVariacao.DoesNotExist:
            return None

    def total_produtos(self):
        """Total de produtos vinculados a esta grade"""
        if self.conta_id:
            return self.produtos_grade.filter(conta_id=self.conta_id).count()
        return self.produtos_grade.count()

    def nome_loja(self):
        """Retorna o nome da grade para a Loja"""
        if self.nome_visivel:
            return self.nome_visivel
        return self.nome


class GradeVariacao(models.Model):
    """Variações de uma grade."""
    id = custom_models.BigAutoField(db_column='grade_variacao_id', primary_key=True)
    id_externo = models.IntegerField(db_column='grade_variacao_id_externo', null=True, default=None)
    nome = models.CharField(db_column='grade_variacao_nome', max_length=255)
    data_criacao = models.DateTimeField(db_column='grade_variacao_data_criacao', auto_now_add=True)
    data_modificacao = models.DateTimeField(db_column='grade_variacao_data_modificacao', auto_now=True, null=True)
    posicao = models.IntegerField(db_column='grade_variacao_posicao', null=True, default=0)
    cor = models.CharField(db_column="grade_variacao_cor", null=True, default=None, max_length=32)
    cor_secundaria = models.CharField(db_column="grade_variacao_cor_secundaria", null=True, default=None, max_length=32)

    grade = models.ForeignKey('catalogo.Grade', related_name='variacoes', on_delete=models.CASCADE)
    conta = models.ForeignKey('plataforma.Conta', related_name='variacoes', null=True)
    contrato = models.ForeignKey('plataforma.Contrato', related_name="variacoes")
    id_anymarket = models.IntegerField(db_column="gradevariacao_id_anymarket", null=True, blank=True)

    class Meta:
        db_table = u"catalogo\".\"tb_grade_variacao"
        verbose_name = u'Variação da grade'
        verbose_name_plural = u'Variações de grade'
        ordering = ['posicao', 'nome']
        unique_together = (("conta", "grade", "nome"),)

    def __unicode__(self):
        return self.nome

    def save(self, *args, **kwargs):
        if self.conta and not self.contrato_id:
            self.contrato_id = self.conta.contrato_id
        super(GradeVariacao, self).save(*args, **kwargs)


class ProdutoManager(models.Manager):

    def get_queryset(self):

        query_quantidade_reservada = 'SELECT COALESCE(SUM(pedido_venda_item_reserva_quantidade),0) ' \
                                     'FROM "pedido"."tb_pedido_venda_item_reserva" WHERE  ' \
                                     '"pedido"."tb_pedido_venda_item_reserva"."produto_id" = "catalogo"."tb_produto"."produto_id"'

        query_categoria_principal_id = 'SELECT "catalogo"."tb_produto_categoria"."categoria_id" ' \
                                       'FROM "catalogo"."tb_produto_categoria" ' \
                                       'WHERE "catalogo"."tb_produto_categoria"."produto_id" = "catalogo"."tb_produto"."produto_id" ' \
                                       'AND "catalogo"."tb_produto_categoria"."produto_categoria_principal" = TRUE'

        return super(ProdutoManager, self).get_queryset().extra({
            'sum_quantidade_reservada': query_quantidade_reservada,
            'categoria_id': query_categoria_principal_id
        })


    """Manager para o produto."""
    def ativos(self):
        return self.listar(somente_ativos=True)

    def disponiveis(self):
        return super(ProdutoManager, self).get_queryset().filter(ativo=True)

    def listar(self, conta_id=None, conta=None, somente_ativos=False,
               somente_disponiveis=False, mostrar_removidos=False,
               somente_removidos=False, excluir_filhos=True,
               select_related=True, prefetch_related=True,
               categoria_principal=None, listagem=None,
               com_descricao=False,
               indisponiveis_por_ultimo=False,
               q=None, distinct=False,
               somente_inativos=False,
               somente_em_espera=False,
               excluir_sob_consulta=False):
        """Filtra apenas os produtos que não são filhos."""
        queryset = super(ProdutoManager, self).get_queryset()

        queryset = queryset.defer("descricao","descricao_completa")

        if excluir_filhos:
            queryset = queryset.exclude(tipo='atributo_opcao')
        if somente_removidos:
            queryset = queryset.filter(removido=True)
        elif somente_ativos:
            queryset = queryset.filter(ativo=True)
        if somente_inativos:
            queryset = queryset.filter(ativo=False)
        # if somente_disponiveis:
        #     queryset = queryset.filter(cache_estoque_disponivel=True)
        if not somente_removidos and not mostrar_removidos:
            queryset = queryset.exclude(removido=True)
        if conta_id:
            queryset = queryset.filter(conta_id=conta_id)
        if conta:
            queryset = queryset.filter(conta=conta)
        if excluir_sob_consulta:
            queryset = queryset.filter(preco__sob_consulta=False)
        if somente_em_espera:
            queryset = queryset.filter(lista_espera__isnull=False).distinct()

        order = []

        # # # Subselects para TUNING!
        # Recupera categoria principal via subselect

        query_categoria_principal_nome = 'SELECT "catalogo"."tb_categoria"."categoria_nome" ' \
                                         'FROM "catalogo"."tb_produto_categoria", "catalogo"."tb_categoria" ' \
                                         'WHERE "catalogo"."tb_produto_categoria"."produto_id" = "catalogo"."tb_produto"."produto_id" ' \
                                         'AND "catalogo"."tb_produto_categoria"."produto_categoria_principal" = TRUE ' \
                                         'AND "catalogo"."tb_produto_categoria"."categoria_id" = "catalogo"."tb_categoria"."categoria_id" LIMIT 1'

        query_imagem_principal = """
            SELECT
                y.imagem_caminho AS caminho
            FROM
                catalogo.tb_produto_imagem x,
                plataforma.tb_imagem y
            WHERE
                x.imagem_id=y.imagem_id
                AND x.produto_id="catalogo"."tb_produto"."produto_id"
            ORDER BY
                x.produto_imagem_posicao,
                x.imagem_id
            LIMIT 1"""

        # Esta linha indica que mostra indisponiveis aqueles que de fato nao estao, por terem a disponibilidade secundaria disponivel.
        # Feito por solicitacao de asana #45159587206562. unattis
        # WHEN x.produto_estoque_quantidade <= 0 AND x.produto_estoque_situacao_sem_estoque >= 0 THEN FALSE

        query_disponibilidade = """
    CASE WHEN "catalogo"."tb_produto"."produto_tipo" = 'normal' THEN
        COALESCE(
            (SELECT (
                CASE
                    WHEN x.produto_estoque_gerenciado = FALSE THEN TRUE
                    WHEN x.produto_estoque_quantidade <= 0 AND x.produto_estoque_situacao_sem_estoque >= 0 THEN FALSE
                    WHEN x.produto_estoque_quantidade >= 1 THEN TRUE
                    ELSE FALSE
                END
            ) FROM catalogo.tb_produto_estoque x WHERE x.produto_id="catalogo"."tb_produto"."produto_id")
        ,FALSE)
    ELSE
        COALESCE(
            (SELECT (
                CASE
                    WHEN x.produto_estoque_gerenciado = FALSE THEN TRUE
                    WHEN x.produto_estoque_quantidade <= 0 AND x.produto_estoque_situacao_sem_estoque >= 0 THEN TRUE
                    WHEN x.produto_estoque_quantidade >= 1 THEN TRUE
                    ELSE FALSE
                END
            ) FROM catalogo.tb_produto_estoque x, catalogo.tb_produto y
            WHERE x.produto_id=y.produto_id
                AND y.produto_id_pai="catalogo"."tb_produto"."produto_id"
                AND y.produto_ativo=TRUE
                ORDER BY 1 DESC
                LIMIT 1
            )
        ,FALSE)
    END"""

        select = {
            'imagem_principal': query_imagem_principal,
            'categoria_principal': query_categoria_principal_nome,
            'disponibilidade_geral': query_disponibilidade
        }

        queryset = queryset.extra(select=select)

        if listagem == 'alfabetica':
            order.append('nome')
        elif listagem == 'ultimos_produtos':
            order.append('-data_criacao')
        elif listagem == 'indisponiveis':
            order.append('disponibilidade_geral')
        elif listagem == 'destaque':
            #if not distinct:
            #    order.append('?')
            #queryset = queryset.filter(destaque=True)
            order.append('-destaque')
        elif listagem == 'mais_vendidos':
            order.append('-vendas')
            subquery = dedent("""\
                COALESCE((
                  SELECT count(pedido_venda_item_id)
                  FROM pedido.tb_pedido_venda_item pvi1
                  LEFT JOIN pedido.tb_pedido_venda pv1 ON
                    (pvi1.pedido_venda_id = pv1.pedido_venda_id)
                  WHERE (pvi1.produto_id = tb_produto.produto_id
                         OR pvi1.produto_id_pai = tb_produto.produto_id)
                    AND pv1.pedido_venda_situacao_id IN
                      (4, 11, 13, 14)
                  GROUP BY pvi1.produto_id_pai
                )::INTEGER, 0)""")
            queryset = queryset.extra(
                select={'vendas': subquery},
                order_by=['-vendas']
            )
        elif listagem == 'ativo':
            order.append('-ativo')
        elif listagem == 'inativo':
            order.append('ativo')

        if order:
            queryset = queryset.order_by(*order)

        if q:
            q = q.strip()
            campos_busca = [
                'modelo__icontains',
                'sku__icontains',
                'nome__icontains',
                'apelido__icontains',
                # retirando a busca na descrição
                # e na descrição da categoria
                # estava causando falsos hits
                # 'descricao__icontains',
                # 'descricao_completa__icontains',
                'produto_categorias__categoria__nome__icontains',
                # 'produto_categorias__categoria__descricao__icontains',
                'marca__nome__icontains',
                'marca__descricao__icontains',
            ]

            if not excluir_filhos:
                campos_busca += [
                    'pai__modelo__icontains',
                    'pai__sku__icontains',
                    'pai__nome__icontains',
                    'pai__apelido__icontains',
                    'pai__produto_categorias__categoria__nome__icontains',
                    'pai__marca__nome__icontains',
                    'pai__marca__descricao__icontains',
                ]

            filtro = []
            for campo in campos_busca:
                filtro.append(Q(**{campo: q}))
            queryset = queryset.filter(reduce(operator.or_, filtro)).distinct()
        if distinct:
            return queryset.distinct()
        return queryset


class Produto(models.Model):
    """Produto da loja virtual."""
    TIPO_NORMAL = 'normal'
    TIPO_ATRIBUTO = 'atributo'
    TIPO_VIRTUAL = 'virtual'
    TIPO_OPCAO = 'atributo_opcao'
    TIPO_KIT = 'kit'

    CHOICES_PRODUTO_TIPOS = [
        (TIPO_NORMAL, u'Produto simples'),
        (TIPO_ATRIBUTO, u'Produto com opções'),
        (TIPO_VIRTUAL, u'Produto virtual'),
        (TIPO_OPCAO, u'Opção'),
        (TIPO_KIT, u'Kit de produtos')
    ]
    TIPOS_LISTAGEM = [
        ('alfabetica', 'Ordem alfabética'),
        ('ultimos_produtos', u'Últimos produtos'),
        ('destaque','Destaque'),
        ('mais_vendidos', 'Mais vendidos'),
        ('indisponiveis', 'Indisponíveis'),
    ]
    CABECALHO_EXPORTACAO = [
        u'SKU',
        u'Sku do produto pai',
        u'Ativo?',
        u'Condição',
        u'Nome produto',
        u'Descrição',
        u'Disponibilidade quando não gerenciar estoque.',
        u"Gerenciar estoque?",
        u"Quantidade",
        u"Disponibilidade dos produtos em estoque",
        u"Disponibilidade quando acabar produtos em estoque.",
        u"Preço custo",
        u"Preço venda",
        u"Preço promocional",
        u"Categoria (nível 1)",
        u"Categoria (nível 2)",
        u"Categoria (nível 3)",
        u"Marca",
        u"Peso (kg)",
        u"Altura (cm)",
        u"Largura (cm)",
        u"Profundidade (cm)",
        u"Link para a foto principal",
        u"Link para foto adicional 1",
        u"Link para foto adicional 2",
        u"Link para foto adicional 3",
        u"URL antiga do produto",
        u"Link do vídeo no Youtube",
    ]

    objects = ProdutoManager()

    id = custom_models.BigAutoField(db_column='produto_id', primary_key=True)
    id_externo = models.IntegerField(db_column="produto_id_externo", null=True)

    nome = models.CharField(db_column='produto_nome', max_length=255, default=None, null=True)
    apelido = models.CharField(db_column='produto_apelido', max_length=255, default=None, null=True)
    descricao = models.TextField(db_column='produto_descricao', default=None, null=True)
    descricao_completa = models.TextField(db_column='produto_descricao_completa', default=None, null=True)
    url_video_youtube = models.CharField(db_column='produto_url_video_youtube', max_length=255, default=None, null=True)

    modelo = models.CharField(db_column='produto_modelo', max_length=255, null=True, default=None)
    sku = models.CharField(db_column='produto_sku', max_length=255, null=True, default=None)
    ncm = models.CharField(db_column='produto_ncm', max_length=10, null=True, blank=True, default=None)
    gtin = models.CharField(db_column='produto_gtin', max_length=14, null=True, blank=True, default=None)
    mpn = models.CharField(db_column='produto_mpn', max_length=70, null=True, blank=True, default=None)
    ativo = models.BooleanField(db_column='produto_ativo', default=False)
    removido = models.BooleanField(db_column='produto_removido', default=False)
    data_criacao = models.DateTimeField(db_column='produto_data_criacao', auto_now_add=True)
    data_modificacao = models.DateTimeField(db_column='produto_data_modificacao', null=True, auto_now=True)
    peso = models.DecimalField(db_column='produto_peso', max_digits=16, decimal_places=3, default=None, null=True)
    altura = models.IntegerField(db_column='produto_altura', default=None, null=True)
    largura = models.IntegerField(db_column='produto_largura', default=None, null=True)
    profundidade = models.IntegerField(db_column='produto_comprimento', default=None, null=True)
    template = models.CharField(db_column='produto_template', max_length=255, null=True, default=None)
    tipo = models.CharField(db_column='produto_tipo', max_length=255, null=True, default=TIPO_NORMAL, choices=CHOICES_PRODUTO_TIPOS)
    bloqueado = models.BooleanField(db_column='produto_bloqueado', default=False, null=False)
    usado = models.BooleanField(db_column='produto_usado', default=False, null=False)

    imagens = models.ManyToManyField('domain.Imagem', through='catalogo.ProdutoImagem', related_name='produtos')
    grades = models.ManyToManyField('catalogo.Grade', through='catalogo.ProdutoGrade', related_name='produtos')
    categorias = models.ManyToManyField('catalogo.Categoria', through='catalogo.ProdutoCategoria', related_name='produtos')
    destaque = models.BooleanField(db_column='produto_destaque', null=False, default=False)

    categoria_global = models.ForeignKey('catalogo.CategoriaGlobal', db_column='categoria_global_id', null=True)
    pai = models.ForeignKey('catalogo.Produto', db_column='produto_id_pai', related_name='filhos', null=True, on_delete=models.CASCADE)
    marca = models.ForeignKey('catalogo.Marca', related_name='produtos', null=True, on_delete=models.SET_NULL)
    conta = models.ForeignKey('plataforma.Conta', related_name='produtos', on_delete=models.CASCADE)
    contrato = models.ForeignKey('plataforma.Contrato', related_name='produtos')
    id_anymarket = models.IntegerField(db_column="produto_id_anymarket", null=True, blank=True)
    id_sku_anymarket = models.IntegerField(db_column="produto_id_sku_anymarket", null=True, blank=True)

    class Meta:
        # app_label = "catalogo"
        db_table = u"catalogo\".\"tb_produto"
        verbose_name = 'Produto'
        verbose_name_plural = 'Produtos'
        ordering = ['-data_criacao']
        unique_together = (("conta", "sku"),)
        get_latest_by = 'id'

    # Mantendo compatibilidade reversa.
    def _get_comprimento(self):
        return self.profundidade

    def _set_comprimento(self, value):
        self.profundidade = value

    comprimento = property(_get_comprimento, _set_comprimento)

    def __unicode__(self):
        return self.nome or ''

    def _validate_unique(self):
        """Valida se o objeto inserido é único para o apelido. Esta função é
        usada apenas quando o objeto é salvo no banco.
        """
        if Produto.objects.exclude(pk=self.pk) \
                .filter(apelido=self.apelido, apelido__isnull=False,
                        conta_id=self.conta_id).count():
            raise ValidationError({'apelido': [u'Um produto com a mesma URL já existe.']})

    def youtube_id(self):
        if self.url_video_youtube:
            return self.url_video_youtube.split('=')[-1]

    def get_path(self):

        urls = self.urls.filter(principal=True)[:1]

        if urls is not None and urls.__len__() > 0 and urls[0]:
            url = urls[0]
        else:
            url = self.url_apelido()

        try:
            string = str(url)
        except UnicodeEncodeError:
            string =  utils.to_ascii(url)

        if string[:1] == '/':
            return string[1:]
        return string

    def get_absolute_url(self, usa_dominio=True):
        url = self.get_path()
        if usa_dominio:
            return "http://{}/{}".format(self.conta.url_dominio, url)
        return url

    def url_apelido(self):
        apelido = self.apelido
        if apelido:
            return "/produto/" + apelido.strip() + ".html";
        return "/produto/" + str(self.id) + ".html"

    def delete(self, *args, **kwargs):
        if self.removido or self.pai:
            return super(Produto, self).delete(*args, **kwargs)
        else:
            self.removido = True
            return self.save()

    def index(self):
        try:
            return self.produto_index.all()[0]
        except:
            return None

    def validate_unique(self, *args, **kwargs):
        if Produto.objects.exclude(pk=self.pk) \
                .filter(sku=self.sku, conta_id=self.conta_id).count():
            raise ValidationError({'sku': [u'Um produto com o código SKU inserido já existe.']})
        super(Produto, self).validate_unique(*args, **kwargs)

    def natural_key(self):
        return self.nome

    def logar(self, codigo, descricao, **kwargs):
        return None

    @classmethod
    def gerar_cabecalho(self):
        return self.CABECALHO_EXPORTACAO + [x.nome for x in
                                            Grade.objects.filter(
                                                conta_id__isnull=True
                                            ).order_by('id')]

    @classmethod
    def criar_rascunho(cls, conta_id, tipo=None):
        timestamp = time.strftime("%Y-%m-%d-%H-%M-%S")
        produto, criado = cls.objects.get_or_create(
            conta_id=conta_id,
            apelido="produto-rascunho-%s" % timestamp,
            tipo=tipo,
            sku="produto-rascunho-%s" % timestamp
        )
        return produto

    def criar_filho(self):
        if self.tipo != 'atributo':
            raise ProdutoNaoPodeTerFilho(
                u'O produto do tipo %s não pode ter filhos.' % self.tipo)

        timestamp = time.strftime("%Y-%m-%d-%H-%M-%S")
        produto_filho = Produto.objects.create(
            ativo=True,
            tipo='atributo_opcao', sku='%s-%s' % (self.sku, timestamp), conta_id=self.conta_id, pai=self)

        return produto_filho

    def disponivel(self):
        """Retorna True caso o produto esteja disponível para venda, caso
        contrário, retorna False.
        """
        return None

    def disponibilidade(self):
        try:
            return self.estoque.disponibilidade()
        except:
            return None

    def quantidade_disponivel(self):
        """Retorna a quantidade disponível para venda."""
        if self.filhos and not self.estoque.quantidade_disponivel():
            return self.estoque.quantidade_disponivel_com_variacao()
        else:
            return self.estoque.quantidade_disponivel()

    def caracteristicas(self):
        """
        Retorn as caracteristicas do produto
        """
        valores = self.caracteristicas_valores.prefetch_related('caracteristica', 'valor').all()
        return [

            {
                'caracteristica': x.caracteristica.nome,
                'valor': x.obter_valor(),
                'posicao': x.caracteristica.posicao,
                'termo': utils.to_ascii('%s__%s__%s' % (x.caracteristica.posicao, x.caracteristica.nome, x.obter_valor()))
            } for x in valores if x.caracteristica.filtrar]


    def nomes_variacoes(self):
        return ' - '.join(['%s: %s' % (x.grade, x.variacao) for x in self.produto_grades_variacoes.all()])


    def csv(self):
        """
        Retorna os dados na ordem para gerar o XLS de saida
        """
        return [
            self.sku,
            'SIM' if self.ativo else u'NÃO',
            self.nome if self.tipo in [Produto.TIPO_NORMAL, Produto.TIPO_ATRIBUTO] else '',
            'SIM' if self.estoque.gerenciado else 'NÃO',
            self.estoque.quantidade,
            utils.formatar_decimal_br(self.preco.custo),
            utils.formatar_decimal_br(self.preco.cheio),
            utils.formatar_decimal_br(self.preco.promocional),
            self.peso,
            self.altura,
            self.largura,
            self.profundidade,
        ]

    def pontuacao(self, conta=None):
        """Retorna a pontuação para o boost do produto
        com base em algumas regras basicas"""
        pontuacao_inicial = 0
        if not conta:
            conta = self.conta
        if not hasattr(conta, '_pontuacao'):
            conta.pontuacao()

        pontuacao_inicial = conta._pontuacao
        vendas = self.pedido_venda_itens.count()
        if vendas:
            pontuacao_inicial += vendas * 0.1
        return pontuacao_inicial

    def gerar_url(self, produto=None, conta=None, relative=False):
        """Gera o permalink(url) do produto"""
        if not conta:
            conta = self.conta

        if not produto:
            produto = self

        if type(produto) == dict:
            apelido = produto['apelido']
            link_produto = reverse('catalogo_produto_detalhar',
                                   kwargs={'apelido': apelido})
            if relative:
                return link_produto
            return 'http://%s%s' % (conta.url_dominio, link_produto)
        else:
            link_produto = produto.get_absolute_url()
            return link_produto

    def json(self, filhos=False, grade=False):
        """ Retorna um dicionario já pronto para ser transformado em JSON """
        preco_loja = self.preco_loja()
        saida = {
            'id': self.id,
            'nome': self.nome,
            'sku': self.sku,
            'estoque': float(str(self.estoque.quantidade_disponivel())),
            'cheio': float(preco_loja.cheio or 0),
            'custo': float(preco_loja.custo or 0),
            'venda': float(preco_loja.promocional or preco_loja.cheio or 0),
            'promocional': float(preco_loja.promocional or 0),
            # 'preco_varia': self.preco_varia(),
            'conta': self.conta_id
        }
        if grade:
            saida['grade'] = dict(([(x.variacao.grade.nome, x.variacao.nome)
                                    for x in self.produto_grades_variacoes.all()]))
        if filhos:
            saida['filhos'] = []
            for filho in self.filhos.filter(ativo=True):
                saida['filhos'].append(filho.json(filhos=False, grade=True))
        return saida

    def serialize(self):
        produto = self
        json = produto.json()

        if produto.pai:
            imagem = produto.pai.imagem()
            json['url'] = self.gerar_url(produto=produto.pai)
            json['nome'] = produto.pai.nome
        else:
            imagem = produto.imagem()
            json['url'] = self.gerar_url(produto=self)

        if imagem:
            json['imagem'] = imagem.caminho
        else:
            json['imagem'] = None

        return json

    def duplicar(self):
        sku = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(9))
        cheio = self.preco.cheio
        custo = self.preco.custo
        promocional = self.preco.promocional
        sob_consulta = self.preco.sob_consulta

        produto = self
        produto.pk = None
        produto.sku = u'{}-{}'.format(self.sku, sku)
        produto.apelido = u'{}-{}'.format(sku.lower(), self.apelido)
        produto.url_video_youtube = None
        # produto.cache_imagem_principal = None

        # if self.cache_url:
        #     produto.cache_url = u'{}-{}'.format(self.cache_url, sku.lower())

        if self.nome and not 'duplicado' in self.nome.lower() :
            produto.nome = u'DUPLICADO - {}'.format(self.nome)

        produto.save()

        categoria = self.categoria()

        if categoria:
            ProdutoCategoria.objects.create(categoria_id=categoria.id, conta=self.conta, produto_id=produto.id)

        try:
            preco = ProdutoPreco.objects.get(produto=produto, conta=self.conta, contrato=self.conta.contrato)
        except ProdutoPreco.DoesNotExist:
            raise ValueError(u'A preço não foi encontrado.')

        preco.cheio = cheio
        preco.custo = custo
        preco.promocional = promocional
        preco.sob_consulta = sob_consulta
        preco.save()

        produto.atualizar_url()

        return produto


    def preco_loja(self):
        """Retorna a instância de preço, se o produto for do tipo atributo
        retorna uma instância não salva preenchida com os menores valores
        possíveis deste produto.
        """
        if self.tipo == 'normal':
            return self.preco
        elif self.tipo == 'atributo':

            preco = ProdutoPreco.objects.extra(
                select={'preco_venda': "(CASE WHEN produto_preco_promocional > 0 THEN produto_preco_promocional ELSE produto_preco_cheio END)"},
                order_by=['preco_venda']).filter(produto__pai_id=self.id, produto__ativo=True)[:1]

            if preco.__len__():
                return preco[0]
            else:
                return None

        else:
            return self.preco


    def seo(self):
        from repositories.marketing.models import SEO

        if not hasattr(self, '_seo'):
            try:
                self._seo = SEO.objects.get(
                    tabela='tb_produto', linha_id=self.id,
                    conta_id=self.conta_id)
            except SEO.DoesNotExist:
                self._seo = None
        return self._seo

    def categoria(self):

        # Nao entendi pq as vezes nao vem!!!
        # Resolver colocando tudo no elasticsearch
        if hasattr(self, "categoria_id") is True:

            try:
                return Categoria.objects.get(id=self.categoria_id)
            except Categoria.DoesNotExist:
                return None

        else:
            tmp = ProdutoCategoria.objects.filter(produto_id=self.id, principal=True)

            if tmp.__len__() > 0:
                return tmp[0].categoria

        return None

    def imagem(self):

        if self.pai_id is not None:
            return None

        from repositories.domain.models import Imagem
        resultado = Imagem.objects.select_related('conta', 'contrato'). \
                        filter(produtos_imagem__produto_id=self.id). \
                        order_by('produtos_imagem__posicao','id')[:1]

        if resultado:
            return resultado[0]

        return None

    def save(self, *args, **kwargs):
        if not self.tipo or self.tipo not in dict(self.CHOICES_PRODUTO_TIPOS):
            self.tipo = self.TIPO_NORMAL

        if self.conta and not self.contrato_id:
            self.contrato_id = self.conta.contrato_id

        try:
            self._validate_unique()
        except ValidationError:
            self.apelido = '%s-%s' % (self.apelido, time.strftime("%Y-%m-%d-%H-%M-%S"))

        super(self.__class__, self).save(*args, **kwargs)

    def vincular_grade(self, grade):
        if isinstance(grade, str) or isinstance(grade, int):
            try:
                grade = Grade.objects.get(
                    Q(conta_id=self.conta_id)|Q(conta_id__isnull=True),
                    pk=grade)
            except Grade.DoesNotExist:
                raise ValueError(u'A grade não foi encontrada.')
        elif not isinstance(grade, Grade):
            raise TypeError(u'A grade deve ser instância de Grade ou o id da ' \
                            u'grade e não "%s".' % grade)
        ProdutoGrade.objects.get_or_create(grade=grade, produto=self, conta=self.conta)
        return True

    def validar_opcao_unica(self, variacoes_ids, produto_filho=None):
        itens = ProdutoGradeVariacao.objects.exclude(produto=produto_filho) \
            .filter(produto_pai=self, variacao_id__in=variacoes_ids).values('produto') \
            .order_by().annotate(total=Count('produto')) \
            .filter(total__gte=len(variacoes_ids))
        return not bool(itens)

    def _validar_opcao(self, valor):
        """Valida o dicionário enviado, ele deve estar no formato esperado."""
        if not isinstance(valor, dict):
            raise TypeError(u'O valor deve ser um dicionário com id da grade e ' \
                            u'nome da variação como valor.')

        valor = dict([(x, y) for x, y in valor.items() if int(x)])
        if len(valor) != self.grades.count():
            raise ValueError(u'A quantidade de variações deve ser igual a ' \
                             u'quantidade de grades relacionadas ao produto: %s' % self.grades.count())

        grades_vinculadas = set([x.id for x in self.grades.all()])
        grades_enviadas = set([x for x in valor.keys()])
        if grades_vinculadas != grades_enviadas:
            raise ValueError(u'As grade enviadas não conferem com as grades ' \
                             u'vinculadas ao produto %s != %s' % (grades_enviadas, grades_vinculadas))

        return True

    def criar_opcao(self, valor):
        """Cria um produto filho e vincula as opções a ele. O parametro valor deve
        ser no formato {id-da-grade: nome-da-variacao}.

        Por exemplo, se a grade 1 é Tamanho e a grade 2 é Cor, você pode enviar:
        {1: 'P', 2: 'Verde'}. Desta forma será criado um novo produto com as
        opções P e Verde vinculadas a ele.
        """
        self._validar_opcao(valor)
        # Criando o produto filho.
        produto_filho = self.criar_filho()
        produto_filho.editar_opcao(valor)
        return produto_filho

    def editar_opcao(self, valor):
        """Edita um produto filho vinculando as novas opções a ele. O parametro
        valor deve ser no formato {id-da-grade: nome-da-variacao}. Este método
        só deve ser chamado de um produto filho.

        Por exemplo, se a grade 1 é Tamanho e a grade 2 é Cor, você pode enviar:
        {1: 'P', 2: 'Verde'}. Desta forma será criado um novo produto com as
        opções P e Verde vinculadas a ele.
        """
        assert self.pai != None
        self.pai._validar_opcao(valor)

        # Vinculando as novas opções.

        for grade_id, nome in valor.items():
            grade = Grade.objects.get(Q(conta_id=self.conta_id) | Q(conta_id__isnull=True), pk=grade_id)
            valor[grade_id] = grade.selecionar_variacao(nome)

        if not self.pai.validar_opcao_unica(valor.values(), produto_filho=self):
            raise IntegrityError(u'Já existe um produto com as opções selecionadas')

        for grade_id, variacao in valor.items():
            ProdutoGradeVariacao.objects.filter(
                Q(conta_id=self.conta_id)|Q(conta_id__isnull=True),
                produto=self,
                grade_id=grade_id).delete()
            produto_grade, criado = ProdutoGrade.objects.get_or_create(
                produto=self.pai, grade_id=grade_id, conta=self.conta)
            produto_grade_variacao, criado = ProdutoGradeVariacao.objects.get_or_create(
                produto=self, produto_pai=self.pai, produto_grade=produto_grade,
                grade_id=grade_id, variacao=variacao, conta=self.conta)

        return True

    class FaltamDadosImportar(Exception):
        pass

    def tem_vendas(self):
        """Verifica se o produto ou seus filhos possuem vendas associadas"""
        from repositories.pedido.models import PedidoVendaItem
        return PedidoVendaItem.objects.filter(Q(produto_id=self.id) | Q(produto_pai_id=self.id)).exists()

    def atualizar_url(self, url=None):
        from repositories.plataforma.models import URL

        if url:
            path_url = url
        else:
            my_url = URL.objects.filter(produto=self, principal=True)[:1]

            if my_url.__len__() > 0:
                url = my_url[0].url
            else:
                if self.apelido is None:
                    self.apelido = '{}'.format(time.strftime("%Y-%m-%d-%H-%M-%S"))

                url = "/{}".format(self.apelido)

            path_url = url

        def criar_url(path_url):
            try:
                url, primeira_url = URL.objects.get_or_create(url=path_url, produto=self, conta=self.conta)
            except IntegrityError as e:
                raise e
            else:
                return url

        def adicionar_traco(s):
            try:
                s.index('.', -5, -1)
                tem_extensao = True
            except ValueError:
                tem_extensao = False

            if tem_extensao:
                l = s.split('.')
                l[-2] = u'%s-' % l[-2]
                s = u'.'.join(l)
            else:
                s = u'%s-' % s

            return s

        contagem = 0
        while True:
            contagem += 1

            # Caso a iteração seja maior que 10 retorna o erro para o lojista.
            if contagem >= 10:
                return False

            try:
                url_obj = criar_url(path_url)
            except IntegrityError as e:
                path_url = adicionar_traco(path_url)
                logger.debug('Erro ao criar URL para produto. (ERRO: %s)' % e)
                continue
            else:
                url_obj.principal = True
                url_obj.save()

                URL.objects.filter(produto=self) \
                    .exclude(pk=url_obj.id) \
                    .update(principal=False)
                break

        return True


    def quantidade_produtos_ativos(self, conta_id, ignorar_id=None):

        produtos = Produto.objects.filter(
            conta_id=conta_id,
            tipo__in=['atributo','normal'],
            ativo=True,
            removido=False,
        )

        if ignorar_id is not None:
            produtos = produtos.exclude(id=ignorar_id)

        return produtos.count()


class ProdutoImagem(models.Model):
    """Imagens de um produto."""
    id = custom_models.BigAutoField(db_column='produto_imagem_id', primary_key=True)
    posicao = models.IntegerField(db_column='produto_imagem_posicao', null=True, default=None)
    principal = models.NullBooleanField(db_column='produto_imagem_principal', null=True, default=False)

    # Os related_name's são "produto_imagens" e "produtos_imagem" pois já existe
    # "imagens" e "produtos" dentro do produto e imagens, respectivamente,
    # referenciando ao ManyToMany de Produto x Imagem.
    produto = models.ForeignKey('catalogo.Produto', related_name='produto_imagens', on_delete=models.CASCADE)
    imagem = models.ForeignKey('domain.Imagem', related_name='produtos_imagem', on_delete=models.CASCADE)
    conta = models.ForeignKey('plataforma.Conta', related_name='produtos_imagens')
    contrato = models.ForeignKey('plataforma.Contrato', related_name='produtos_imagens')
    id_anymarket = models.IntegerField(db_column="produto_imagem_id_anymarket", null=True, blank=True)

    class Meta:
        db_table = u'catalogo\".\"tb_produto_imagem'
        verbose_name = u'Imagem do produto'
        verbose_name_plural = u'Imagens dos produtos'
        ordering = ['produto', '-principal', 'posicao', 'id']

    def __unicode__(self):
        return unicode(self.id)

    def save(self, *args, **kwargs):
        if self.conta and not self.contrato_id:
            self.contrato_id = self.conta.contrato_id
        return super(ProdutoImagem, self).save(*args, **kwargs)


    @classmethod
    def ordenar(cls, imagens_ids, conta_id):
        contador = 0
        cls.objects.filter(imagem_id__in=imagens_ids).update(principal=False)
        for imagem_id in imagens_ids:
            principal = False
            if contador == 0:
                principal = True
            total = cls.objects.filter(imagem_id=imagem_id, conta_id=conta_id) \
                .update(posicao=contador, principal=principal)
            if total:
                contador += 1

    def tamanhos(self):
        if self.imagem:
            return {
                'caminho': self.imagem.caminho
            }


class ProdutoListaEspera(models.Model):
    id = custom_models.BigAutoField(db_column="produto_lista_espera_id", primary_key=True)
    nome = models.CharField(db_column="produto_lista_espera_nome", max_length=256)
    email = models.CharField(db_column="produto_lista_espera_email", max_length=256)
    data_solicitacao = models.DateTimeField(db_column="produto_lista_espera_data_solicitacao", auto_now_add=True)
    produto = models.ForeignKey('catalogo.Produto', db_column="produto_id", related_name='lista_espera')
    conta = models.ForeignKey('plataforma.Conta', related_name='produtos_lista_espera')
    contrato = models.ForeignKey('plataforma.Contrato', related_name='produtos_lista_espera')

    class Meta:
        db_table = u'catalogo\".\"tb_produto_lista_espera'
        verbose_name = u'Avise-me por Produto'
        verbose_name_plural = u'Avise-me por Produtos'
        ordering = ['data_solicitacao']


class ProdutoPreco(models.Model):
    """Preço de um produto."""
    id = custom_models.BigAutoField(db_column='produto_preco_id', primary_key=True)
    cheio = models.DecimalField(db_column='produto_preco_cheio', max_digits=16, decimal_places=4, null=True)
    promocional = models.DecimalField(db_column='produto_preco_promocional', max_digits=16, decimal_places=4, null=True)
    custo = models.DecimalField(db_column='produto_preco_custo', max_digits=16, decimal_places=4, null=True)
    sob_consulta = models.BooleanField(db_column='produto_preco_sob_consulta', default=False)

    moeda = models.ForeignKey('domain.Moeda', related_name='produtos_preco', default='BRL')
    produto = models.OneToOneField('catalogo.Produto', related_name='preco', on_delete=models.CASCADE)
    conta = models.ForeignKey('plataforma.Conta', related_name='produtos_preco')
    contrato = models.ForeignKey('plataforma.Contrato', related_name='produtos_preco')

    class Meta:
        db_table = u'catalogo\".\"tb_produto_preco'
        verbose_name = u'Preço do produto'
        verbose_name_plural = u'Preços dos Produtos'
        ordering = ['id']

    def __unicode__(self):
        return unicode(self.id)

    def _get_preco_cheio(self):
        return self.cheio

    def _set_preco_cheio(self, value):
        self.cheio = value

    preco_cheio = property(_get_preco_cheio, _set_preco_cheio)

    def _get_preco_promocional(self):
        return self.promocional

    def _set_preco_promocional(self, value):
        self.promocional = value

    preco_promocional = property(_get_preco_promocional, _set_preco_promocional)

    def _get_preco_custo(self):
        return self.custo

    def _set_preco_custo(self, value):
        self.custo = value

    preco_custo = property(_get_preco_custo, _set_preco_custo)

    def _verificar_preenchimento(self):
        return bool(self.cheio or self.promocional)

    def preenchido(self):
        """Retorna True caso o preço tenha sido preenchido, se não,
        retorna False.
        """
        return bool(self.cheio or self.promocional)

    def formatado_para_orcamento(self):
        if self.sob_consulta:
            return "Consulte-nos"
        if self.promocional:
            return "R$ {}".format(utils.formatar_decimal_br(self.preco_cheio), utils.formatar_decimal_br(self.preco_promocional))
        if self.preco_cheio:
            return "R$ {}".format(utils.formatar_decimal_br(self.preco_cheio))
        return "Indisponível"

    def save(self, *args, **kwargs):
        # inverter valores
        if self.promocional > self.cheio:
            self.cheio, self.promocional = self.promocional, self.cheio
        elif self.promocional == self.cheio:
            self.promocional = None

        if self.conta and not self.contrato_id:
            self.contrato_id = self.conta.contrato_id

        return super(ProdutoPreco, self).save(*args, **kwargs)


class ProdutoGrade(models.Model):
    """Relação entre produto e grade."""
    id = custom_models.BigAutoField(db_column='produto_grade_id', primary_key=True)
    posicao = models.IntegerField(db_column='produto_grade_posicao', default=0)

    produto = models.ForeignKey('catalogo.Produto', related_name='produto_grades', on_delete=models.CASCADE)
    grade = models.ForeignKey('catalogo.Grade', related_name='produtos_grade', on_delete=models.CASCADE)
    conta = models.ForeignKey('plataforma.Conta', related_name='produtos_grades')
    contrato = models.ForeignKey('plataforma.Contrato', related_name='produtos_grades')

    class Meta:
        db_table = u"catalogo\".\"tb_produto_grade"
        verbose_name = u'Grade de um produto'
        verbose_name_plural = u"Grades dos produtos"
        ordering = ['produto', 'grade']
        unique_together = (("produto", "grade"), )

    def __unicode__(self):
        return unicode(self.id)

    def save(self, *args, **kwargs):
        if self.conta and not self.contrato_id:
            self.contrato_id = self.conta.contrato_id
        return super(ProdutoGrade, self).save(*args, **kwargs)


class ProdutoGradeVariacao(models.Model):
    """Relação entre produto e as variações da grade."""
    id = custom_models.BigAutoField(db_column='produto_grade_variacao_id', primary_key=True)
    produto = models.ForeignKey('catalogo.Produto', related_name='produto_grades_variacoes', on_delete=models.CASCADE)
    produto_pai = models.ForeignKey('catalogo.Produto', db_column='produto_id_pai', related_name='produto_grades_variacoes_filhos', on_delete=models.CASCADE)
    produto_grade = models.ForeignKey('catalogo.ProdutoGrade', related_name='produto_grades_variacoes', on_delete=models.CASCADE)
    grade = models.ForeignKey('catalogo.Grade', related_name='produtos_grade_variacoes', on_delete=models.CASCADE)
    variacao = models.ForeignKey('catalogo.GradeVariacao', db_column="grade_variacao_id", related_name='produtos_grade_variacoes', on_delete=models.CASCADE)
    conta = models.ForeignKey('plataforma.Conta', related_name='produtos_grades_variacoes')
    contrato = models.ForeignKey('plataforma.Contrato', related_name='produtos_grades_variacoes')
    id_grade_anymarket = models.IntegerField(db_column="produtograde_id_grade_anymarket", null=True, blank=True)
    id_variacao_anymarket = models.IntegerField(db_column="produtogrades_id_variacao_anymarket", null=True, blank=True)

    class Meta:
        db_table = u"catalogo\".\"tb_produto_grade_variacao"
        verbose_name = u'Variação da grade de um produto'
        verbose_name_plural = u"Variações das grades dos produtos"
        ordering = ['grade', 'variacao']

    def __unicode__(self):
        return unicode(self.id)

    def save(self, *args, **kwargs):
        if self.conta and not self.contrato_id:
            self.contrato_id = self.conta.contrato_id
        return super(ProdutoGradeVariacao, self).save(*args, **kwargs)


class ProdutoGradeVariacaoImagem(models.Model):

    id = custom_models.BigAutoField(db_column="produto_grade_variacao_imagem_id", primary_key=True)

    produto = models.ForeignKey('catalogo.Produto', related_name='produto_grades_imagens', on_delete=models.CASCADE)
    variacao = models.ForeignKey('catalogo.GradeVariacao', db_column="grade_variacao_id", related_name='grade_variacao_id', on_delete=models.CASCADE)
    imagem = models.ForeignKey('domain.Imagem', related_name='produtos_grade_imagem', on_delete=models.CASCADE)
    conta = models.ForeignKey('plataforma.Conta', related_name='produto_grades_imagens')
    contrato = models.ForeignKey('plataforma.Contrato', related_name='produto_grades_imagens')

    class Meta:
        db_table = u"catalogo\".\"tb_produto_grade_variacao_imagem"
        verbose_name = u'Imagem da grade do Produto'
        verbose_name_plural = u'Imagens das grades dos produtos'
        unique_together = (("conta", "variacao", "produto"),)

    def save(self, *args, **kwargs):
        if self.conta and not self.contrato_id:
            self.contrato_id = self.conta.contrato_id
        return super(ProdutoGradeVariacaoImagem, self).save(*args, **kwargs)


class ProdutoCategoria(models.Model):
    """Relação entre produto e categoria."""
    id = custom_models.BigAutoField(db_column='produto_categoria_id', primary_key=True)
    principal = models.BooleanField(db_column='produto_categoria_principal', default=False)

    produto = models.ForeignKey('catalogo.Produto', related_name='produto_categorias', on_delete=models.CASCADE)
    categoria = models.ForeignKey('catalogo.Categoria', related_name='produtos_categoria', on_delete=models.CASCADE)
    conta = models.ForeignKey('plataforma.Conta', related_name='produtos_categorias')
    contrato = models.ForeignKey('plataforma.Contrato', related_name='produtos_categorias')

    class Meta:
        db_table = u"catalogo\".\"tb_produto_categoria"
        verbose_name = u'Categoria de um produto'
        verbose_name_plural = u"Categorias dos produtos"
        ordering = ['id']
        unique_together = (("produto", "categoria"), )

    def __unicode__(self):
        return unicode(self.id)

    def save(self, *args, **kwargs):
        if self.conta and not self.contrato_id:
            self.contrato_id = self.conta.contrato_id
        return super(ProdutoCategoria, self).save(*args, **kwargs)


class ProdutoEstoque(models.Model):
    """Estoque de um produto."""
    SITUACAO_INDISPONIVEL = -1
    SITUACAO_DISPONIVEL = 0

    SITUACOES = [
        (SITUACAO_INDISPONIVEL, u'Indiponível'),
        (SITUACAO_DISPONIVEL, u'Diponível'),
    ]

    id = custom_models.BigAutoField(db_column='produto_estoque_id', primary_key=True)
    gerenciado = models.BooleanField(db_column='produto_estoque_gerenciado', default=False)
    quantidade = models.DecimalField(db_column='produto_estoque_quantidade', max_digits=16, decimal_places=4, default=0)
    situacao_em_estoque = models.IntegerField(db_column='produto_estoque_situacao_em_estoque', default=0)
    situacao_sem_estoque = models.IntegerField(db_column='produto_estoque_situacao_sem_estoque', default=0)

    produto = models.OneToOneField('catalogo.Produto', related_name='estoque', on_delete=models.CASCADE)
    conta = models.ForeignKey('plataforma.Conta', related_name='produtos_estoque')
    contrato = models.ForeignKey('plataforma.Contrato', related_name='produtos_estoques')
    id_anymarket = models.IntegerField(db_column="produto_estoque_id_anymarket", null=True, blank=True)

    class Meta:
        db_table = u"catalogo\".\"tb_produto_estoque"
        verbose_name = u'Estoque do Produto'
        verbose_name_plural = u"Estoque dos Produtos"
        ordering = ['id']


    def logar(self, codigo, descricao, **kwargs):
        return None
        # descricao = u"%s (id=%s, produto_id=%s)" % (
        #     descricao, self.id, self.produto_id)
        # return NoSQLLog(codigo=codigo, conta_id=self.conta_id,
        #                 descricao=descricao, **kwargs).save()

    def save(self, *args, **kwargs):
        if not self.quantidade:
            self.quantidade = 0

        if self.conta and not self.contrato_id:
            self.contrato_id = self.conta.contrato_id

        super(self.__class__, self).save(*args, **kwargs)

    def _get_estoque_gerenciado(self):
        return self.gerenciado

    def _set_estoque_gerenciado(self, value):
        self.gerenciado = value

    estoque_gerenciado = property(_get_estoque_gerenciado, _set_estoque_gerenciado)

    def _get_estoque_quantidade(self):
        return self.quantidade

    def _set_estoque_quantidade(self, value):
        self.quantidade = value

    estoque_quantidade = property(_get_estoque_quantidade, _set_estoque_quantidade)

    def _verificar_disponibilidade(self):
        """Retorna True caso o produto está disponível para a venda, False caso contrário."""
        # Sempre que o em_estoque está indisponível, quer dizer que o produto
        # está indisponível independente de qualquer outra verificação.
        if self.situacao_em_estoque <= self.SITUACAO_INDISPONIVEL:
            return False
        if self.situacao_em_estoque >= self.SITUACAO_DISPONIVEL:
            # Quando o estoque é gerenciado, a quantidade deve ser analisada.
            if not self.gerenciado or (self.gerenciado and self.quantidade_disponivel() > 0):
                return True
            # Somente quando o estoque é gerenciado e a quantidade for menor que
            # zero que o sem_estoque é levado em consideração.
            elif self.gerenciado and self.quantidade_disponivel() <= 0 and \
                            self.situacao_sem_estoque == self.SITUACAO_INDISPONIVEL:
                return False

        # Em qualquer outra combinação o produto estará disponível.
        return True

    def quantidade_disponivel(self):
        """Retorna a quantidade disponível para venda."""

        if hasattr(self.produto, 'sum_quantidade_reservada'):
            return self.quantidade - self.produto.sum_quantidade_reservada

        else:
            return self.quantidade

    def quantidade_disponivel_com_variacao(self):
        """Retorna a quantidade disponível para venda do produto com variação."""
        quantidade = sum([x.estoque.quantidade for x in self.produto.filhos.all() if x.estoque.quantidade])

        if hasattr(self, 'sum_quantidade_reservada'):
            return quantidade - self.sum_quantidade_reservada
        else:
            return quantidade

    def disponivel(self):
        """Retorna True caso o produto esteja disponível para compra, se não, False."""
        return self._verificar_disponibilidade()

    def disponibilidade(self):
        """Retorna a disponibilidade em dias. 0 é imediato e -1 é indisponível."""
        if hasattr(self, 'quantidade_loja'):
            quantidade_loja = self.quantidade_loja
        else:
            quantidade_loja = 0
        if self.produto.tipo == 'atributo':
            return None

        quantidade_disponivel = self.quantidade_disponivel()
        if quantidade_loja > quantidade_disponivel and self.situacao_sem_estoque > 0:
            return self.situacao_sem_estoque
        if self.situacao_em_estoque == self.SITUACAO_INDISPONIVEL or \
                not self.gerenciado or (self.gerenciado and quantidade_disponivel > 0):
            return self.situacao_em_estoque
        else:
            return self.situacao_sem_estoque

    def equalizar(self, quantidade=None, motivo=None):
        """Equaliza a quantidade de itens no estoque."""
        self.quantidade = quantidade
        self.save()

        # self.logar('LPN09003', u'Estoque equalizado.')

    def incrementar(self, quantidade=None, motivo=None):
        """Adiciona a quantidade passada a quantidade de itens no estoque."""
        self.quantidade = self.quantidade + quantidade
        self.save()

        # self.logar('LPN09001', u'Estoque adicionado.')

    def reduzir(self, quantidade=None, motivo=None, pedido_venda=None):
        """Reduz a quantidade de itens no estoque. Caso o pedido_venda seja
        enviado, a quantidade é descartada e o pedido_venda será usado para
        identificar a quantidade a ser reduzida.
        """
        if pedido_venda:
            pedido_item = pedido_venda.itens.get(produto=self.produto)
            # Sobrescreve a quantidade que será reduzida.
            quantidade = pedido_item.quantidade

        self.quantidade = self.quantidade - quantidade
        self.save()

        # self.logar('LPN09002', u'Estoque removido.')

    decrementar = reduzir


class CategoriaGlobal(MPTTModel):

    id = custom_models.BigAutoField(db_column='categoria_global_id', primary_key=True)
    nome = models.CharField(db_column='categoria_global_nome', max_length=128, null=False)
    data_criacao = models.DateTimeField(
        db_column="categoria_global_data_criacao", auto_now_add=True)
    data_modificacao = models.DateTimeField(
        db_column="categoria_global_data_modificacao", auto_now=True)
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children')

    objects = TreeManager()

    class Meta:
        db_table = u"catalogo\".\"tb_categoria_global"
        verbose_name = u'Categoria global'
        verbose_name_plural = u'Categorias globais'

    def __unicode__(self):
        try:
            return self.nome
        except:
            return '-'

    def separador_level(self, separador='--- '):
        if self.level:
            return separador * self.level
        return ''

    @property
    def count_children(self):
        if not hasattr(self, '_count_children'):
            self._count_children = len(self.get_children())
        return self._count_children

    @property
    def caracteristica(self, only=None):
        if not hasattr(self, '_caracteristica'):
            try:
                if only:
                    self._caracteristica = self.caracteristicas.only(*only).all()[0]
                else:
                    self._caracteristica = self.caracteristicas.all()[0]
            except IndexError:
                self._caracteristica = None
        return self._caracteristica


class Caracteristica(models.Model):

    TIPOS_FILTROS = [
        ('opcoes', u'Opções'),
        ('boleano', u'Sim/Não'),
        ('estado', u'Estado'),
        ('cidade', u'Cidade'),
        ('bairro', u'Bairro'),
    ]

    id = custom_models.BigAutoField(db_column='caracteristica_id', primary_key=True)
    tipo = models.CharField(db_column='caracteristica_tipo', max_length=32)
    posicao = models.IntegerField(db_column='caracteristica_posicao', default=0)
    filtrar = models.BooleanField(db_column='caracteristica_pode_filtrar', default=False)
    data_criacao = models.DateTimeField(db_column="caracteristica_data_criacao", auto_now_add=True)
    data_modificacao = models.DateTimeField(db_column="caracteristica_data_modificacao", auto_now=True)
    categoria_global = models.ForeignKey('catalogo.CategoriaGlobal', related_name='caracteristicas', db_column='categoria_global_id')
    nome = models.CharField(db_column='caracteristica_nome', max_length=128, null=False)

    class Meta:
        db_table = u"catalogo\".\"tb_caracteristica"
        verbose_name = u'Caracteristica'
        verbose_name_plural = u'Caracteristicas'
        ordering = ['posicao', 'id']

    def __unicode_(self):
        return str(self.id)

    def identificador(self):
        """
        Função simples só para não colocar muita lógica no template
        ele retorna o tipo do produto se o mesmo for bairro, cidade ou estado
        caso contrario ele retorna o id_ + self.id
        """
        if self.tipo in ['bairro', 'cidade', 'estado']:
            nome = self.tipo
        else:
            nome = self.id
        return 'id_%s' % nome

    def valor_custom(self):
        if self.tipo in ['bairro', 'cidade', 'texto', 'estado']:
            return True
        return False


class CaracteristicaValor(models.Model):

    id = custom_models.BigAutoField(db_column='caracteristica_valor_id', primary_key=True)
    valor = models.CharField(db_column='caracteristica_valor_valor', max_length=64, null=False)
    idioma = models.ForeignKey('domain.Idioma', related_name='categorias_globais_filtros_opcoes', default='pt-br')
    caracteristica = models.ForeignKey('catalogo.Caracteristica', db_column='caracteristica_id', related_name='valores')

    class Meta:
        db_table = u"catalogo\".\"tb_caracteristica_valor"
        verbose_name = u'Valor da caracteristica'
        verbose_name_plural = u'Valores das caracteristicas'
        ordering = ['valor']

    def __unicode__(self):
        return self.valor


class ProdutoCaracteristicaValor(models.Model):
    id = custom_models.BigAutoField(db_column='produto_caracteristica_valor_id', primary_key=True)
    produto = models.ForeignKey('catalogo.Produto', db_column='produto_id', related_name='caracteristicas_valores')
    categoria_global = models.ForeignKey('catalogo.CategoriaGlobal', db_column='categoria_global_id', related_name='produtos_caracteristicas')
    caracteristica = models.ForeignKey('catalogo.Caracteristica', db_column='caracteristica_id', related_name='produtos_caracteristica')
    valor = models.ForeignKey('catalogo.CaracteristicaValor', db_column='caracteristica_valor_id', null=True, related_name='produtos')
    texto = models.CharField(max_length=128, db_column='caracteristica_valor_texto', null=True)

    conta = models.ForeignKey('plataforma.Conta', db_column='conta_id', related_name='produtos_opcoes')

    contrato = models.ForeignKey('plataforma.Contrato', related_name="produtos_opcoes", null=True, blank=True)

    class Meta:
        db_table = u'catalogo"."tb_produto_caracteristica_valor'
        verbose_name = u'Produto categoria global opcao'
        verbose_name_plural = u'Produtos categorias globais opções'

    def save(self, *args, **kwargs):
        if not self.contrato_id and self.conta:
            self.contrato_id = self.conta.contrato_id
        super(ProdutoCaracteristicaValor, self).save(*args, **kwargs)

    def obter_valor(self):
        """
        Retorna o valor do caracteristica definida para o produto
        baseando-se na seguinte regra:

        Se tiver texto definido (quer dizer que a caracteristica quem deve preencheer é o lojista)
        deve ser retornado o texto, caso contrario retorna o valor de CaracteristicaValor atribuida
        """
        return self.texto if self.texto else self.valor.valor


@receiver(post_save, sender=Produto)
def produto_post_save(sender, instance, created, raw, **kwargs):
    from repositories.marketing.models import SEO
    from repositories.plataforma.models import URL

    # Cria as relações que o produto precisa para funcionar.
    if created and not getattr(instance, '_copia', False):

        # Estoque e preco somente para produto de fato
        # tipo 'atributo' nao deve ter preco e estoque. Adicionado para manter retrocompatili
        if instance.tipo in ('normal','atributo','atributo_opcao'):

            ProdutoEstoque.objects.create(
                contrato_id=instance.contrato_id, conta_id=instance.conta_id, produto_id=instance.id)

            ProdutoPreco.objects.create(
                contrato_id=instance.contrato_id, conta_id=instance.conta_id, produto_id=instance.id)

        # SEO para produto prinicpal ou atributo que agrupa as opcoes disponíveis
        if instance.tipo in ('normal', 'atributo'):
            SEO.objects.create(
                contrato_id=instance.contrato_id, conta_id=instance.conta_id,
                linha_id=instance.id, tabela='tb_produto')

            # Criando URL para os produtos. É necessário excluir o produto
            # rascunho pois ele foi recém criado e não precisa de URL.
            # Esta suposição foi baseada no modelo do AppPainel antigo.
            if instance.sku.startswith(u'produto-rascunho-'):
                # Slufigy da URL
                url_slugify = '/' + slugify(u'{}-{}'.format(remover_acentos(instance.nome), instance.id))

                URL.objects.create(
                    contrato_id=instance.contrato_id, conta_id=instance.conta_id, produto_id=instance.id,
                    principal=True, url=url_slugify
                )


@receiver(post_save, sender=ProdutoCategoria)
def produto_categoria_post_save(sender, instance, created, raw, **kwargs):

    if instance.principal is True:

        total = ProdutoCategoria.objects.filter(
            ~Q(categoria_id=instance.categoria_id), produto_id=instance.produto_id, principal=True).count()

        # Se tem outra categoria como principal e esta esta para ser, desmarcar a anterior
        if total > 0:
            ProdutoCategoria.objects.filter(
                ~Q(categoria_id=instance.categoria_id), produto_id=instance.produto_id, principal=True).\
                update(principal=False)


@receiver(post_save, sender=Categoria)
def categoria_post_save(sender, instance, created, raw, **kwargs):
    from repositories.marketing.models import SEO
    from repositories.plataforma.models import URL

    if created:
        SEO.objects.create(
            contrato_id=instance.contrato_id, conta_id=instance.conta_id, linha_id=instance.id, tabela='tb_categoria')

        # Slufigy da URL
        url_slugify = '/' + slugify(u'{}-{}'.format(remover_acentos(instance.nome),instance.id))

        URL.objects.create(
            contrato_id=instance.contrato_id, conta_id=instance.conta_id, categoria_id=instance.id,
            principal=True, url=url_slugify
        )


# Caso apelido nao seja passado, cria.
# Este recurso pode ser eliminado após iniciar o uso da tabela de URL
@receiver(post_save, sender=Marca)
def marca_post_save(sender, instance, created, raw, **kwargs):

    # Cria as relações que o produto precisa para funcionar.
    if created and instance.apelido is None:

        # Slufigy da URL
        url_slugify = slugify('{}-{}'.format(remover_acentos(instance.nome),instance.id))

        instance.apelido = url_slugify
        instance.save()


@receiver(post_save, sender=Caracteristica)
def caracteristica_post_save(sender, instance, created, raw, **kwargs):
    if instance.tipo == 'boleano' and created:
        valores = [u'Sim', u'Não']
        for valor in valores:
            CaracteristicaValor.objects.create(
                idioma_id='pt-br', caracteristica_id=instance.id,
                valor=valor
            )


class AnymarketStatus(models.Model):

    conta = models.ForeignKey(
        'plataforma.Conta',
        db_column="conta_id",
        related_name="anymarket_conta_id"
    )
    modelo = models.CharField(verbose_name="modelo", max_length=50, null=True, blank=True)
    id_modelo = models.IntegerField(verbose_name='id do modelo', null=True, blank=True)
    status = models.CharField(verbose_name='status', max_length=50, null=True, blank=True)
    mensagem = models.TextField(verbose_name='mensagem', null=True, blank=True)
    data_modificacao = models.DateTimeField(verbose_name='data da modificacao', auto_now=True)

    class Meta:
        db_table = u"catalogo\".\"tb_anymarket_status"
        verbose_name = "AnymarketStatus"
        verbose_name_plural = "AnymarketStatuss"

    def __unicode__(self):
        return "{}/{}-{}".format(
            self.modelo,
            self.id,
            self.mensagem)
