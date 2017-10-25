# -*- coding: utf-8 -*-

from trytond.model import ModelView, ModelSQL, fields
from trytond.pool import Pool, PoolMeta
from trytond import backend
from sql.conditionals import Case
from sql.functions import Substring, DateTrunc, CharLength
from trytond.transaction import Transaction
from sqlextension import Replace, Concat2
import logging

logger = logging.getLogger(__name__)

# objektklassen auflisten
__all__ = ['PimMemo']
__metaclass__ = PoolMeta


class PimMemo(ModelSQL, ModelView):
    "PimMemo" 
    __name__ = "pim_memos.note"

    name = fields.Function(fields.Char(string=u'Name', readonly=True), 
            'get_info', searcher='search_name')
    title = fields.Char(string=u'Title', help=u'Title for the note (can be left blank)', select=True)
    memo = fields.Text(string=u'Memo', required=True, select=True)
    memoshort = fields.Function(fields.Text(string=u'Memo', readonly=True), 
            'get_info', searcher='search_memoshort')
    category = fields.Many2One('pim_memos.category', 'Category', ondelete='RESTRICT')

    # hierarchy
    parent = fields.Many2One('pim_memos.note', string=u'Parent', select=True)
    childs = fields.One2Many('pim_memos.note', 'parent', string=u'Children')

    # info
    datecreated = fields.Function(fields.Date(string=u'created', readonly=True), 
            'get_info', searcher='search_datecreated')
    datechanged = fields.Function(fields.Date(string=u'changed', readonly=True), 
            'get_info', searcher='search_datechanged')
    
    @classmethod
    def __register__(cls, module_name):
        super(PimMemo, cls).__register__(module_name)
        TableHandler = backend.get('TableHandler')
        cursor = Transaction().cursor
        # create index for 'create_date' + 'write_date'
        try :
            table = TableHandler(cursor, cls, module_name)
            table.index_action('create_date', action='add')
            table.index_action('write_date', action='add')
        except :
            logger.warning('PimMemo.__register__: index not created!')

    @classmethod
    def validate(cls, memos):
        super(PimMemo, cls).validate(memos)
        cls.check_recursion(memos, rec_name='name')

    @staticmethod
    def order_memoshort(tables):
        table, _ = tables[None]
        return [table.memo]
    
    @staticmethod
    def order_name(tables):
        table, _ = tables[None]
        return [Case(((table.title == None) | (table.title == ''), table.memo), else_=table.title)]

    @staticmethod
    def order_datecreated(tables):
        table, _ = tables[None]
        return [table.create_date]
    
    @staticmethod
    def order_datechanged(tables):
        table, _ = tables[None]
        return [table.write_date]

    @classmethod
    def get_info_sql(cls):
        """ sql-code for query of title
        """
        tab_memo = cls.__table__()
        
        qu1 = tab_memo.select(tab_memo.id.as_('id_memo'),
                Case(
                    ((tab_memo.title == None) | (tab_memo.title == ''), 
                        Substring(Replace(tab_memo.memo, '\n', '; '), 1, 35)),
                    else_ = tab_memo.title
                ).as_('title'),
                DateTrunc('day', tab_memo.create_date).as_('created'),
                DateTrunc('day', tab_memo.write_date).as_('changed'),
                tab_memo.memo.as_('memofull'),
                Case (
                    (CharLength(tab_memo.memo) > 40,
                     Concat2(Substring(Replace(tab_memo.memo, '\n', '; '), 1, 40), '...')
                    ),
                    else_ = Replace(tab_memo.memo, '\n', '; ')
                ).as_('memoshort'),
            )
        return qu1

    @classmethod
    def search_datecreated(cls, name, clause):
        """ search in created
        """
        tab_name = cls.get_info_sql()
        Operator = fields.SQL_OPERATORS[clause[1]]
        
        qu1 = tab_name.select(tab_name.id_memo,
                where=Operator(tab_name.created, clause[2])
            )
        return [('id', 'in', qu1)]
        
    @classmethod
    def search_datechanged(cls, name, clause):
        """ search in changed
        """
        tab_name = cls.get_info_sql()
        Operator = fields.SQL_OPERATORS[clause[1]]
        
        qu1 = tab_name.select(tab_name.id_memo,
                where=Operator(tab_name.changed, clause[2])
            )
        return [('id', 'in', qu1)]
        
    @classmethod
    def search_memoshort(cls, name, clause):
        """ search in memo + title
        """
        tab_name = cls.get_info_sql()
        Operator = fields.SQL_OPERATORS[clause[1]]
        
        qu1 = tab_name.select(tab_name.id_memo,
                where=Operator(tab_name.memofull, clause[2]) | Operator(tab_name.title, clause[2])
            )
        return [('id', 'in', qu1)]
        
    @classmethod
    def search_name(cls, name, clause):
        """ sql-code for search
        """
        tab_name = cls.get_info_sql()
        Operator = fields.SQL_OPERATORS[clause[1]]
        
        qu1 = tab_name.select(tab_name.id_memo,
                where=Operator(tab_name.title, clause[2])
            )
        return [('id', 'in', qu1)]

    @classmethod
    def get_info(cls, memos, names):
        """ get dates, name for memo, from title or content
        """
        cursor = Transaction().cursor
        tab_memo = cls.get_info_sql()
        name_ids = [x.id for x in memos]
        
        # prepare result
        erg1 = {'name': {}, 'datecreated': {}, 'datechanged': {}, 'memoshort': {}}
        for i in name_ids:
            erg1['name'][i] = None
            erg1['datecreated'][i] = None
            erg1['datechanged'][i] = None
            erg1['memoshort'][i] = None
        
        # query
        qu1 = tab_memo.select(tab_memo.id_memo,
                tab_memo.title,
                tab_memo.created,
                tab_memo.changed,
                tab_memo.memoshort,
                where=tab_memo.id_memo.in_(name_ids)
            )
        cursor.execute(*qu1)
        l1 = cursor.fetchall()
        for i in l1:
            (id1, txt1, crdat, chdat, memosh) = i
            erg1['name'][id1] = txt1
            erg1['memoshort'][id1] = memosh
            if not isinstance(crdat, type(None)):
                erg1['datecreated'][id1] = crdat.date()
            if not isinstance(chdat, type(None)):
                erg1['datechanged'][id1] = chdat.date()
        
        # remove not wanted infos
        for i in erg1.keys():
            if not i in names:
                del erg1[i]

        return erg1

# ende PimMemo
