# -*- coding: utf-8 -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2017 Lance Edgar
#
#  This file is part of Rattail.
#
#  Rattail is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  Rattail is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
#  details.
#
#  You should have received a copy of the GNU General Public License along with
#  Rattail.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
Models for vendor catalog batches
"""

from __future__ import unicode_literals, absolute_import

import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declared_attr

from rattail.db.model import Base, Vendor, Product, FileBatchMixin, BatchRowMixin
from rattail.db.types import GPCType


class VendorCatalog(FileBatchMixin, Base):
    """
    Vendor catalog, the source data file of which has been provided by a user,
    and may be further processed in some site-specific way.
    """
    __tablename__ = 'vendor_catalog'
    __batchrow_class__ = 'VendorCatalogRow'

    @declared_attr
    def __table_args__(cls):
        return cls.__default_table_args__() + (
            sa.ForeignKeyConstraint(['vendor_uuid'], ['vendor.uuid'],
                                    name='vendor_catalog_fk_vendor'),
            )

    parser_key = sa.Column(sa.String(length=100), nullable=False, doc="""
    The key of the parser used to parse the contents of the data file.
    """)

    vendor_uuid = sa.Column(sa.String(length=32), nullable=False)

    vendor = relationship(Vendor, doc="""
    Reference to the :class:`Vendor` to which the catalog pertains.
    """)

    effective = sa.Column(sa.Date(), nullable=True, doc="""
    General effective date for the catalog, as determined by the data file.  Note
    that not all catalog files will include this; also, some catalogs include
    effective dates on a per-product basis.
    """)


class VendorCatalogRow(BatchRowMixin, Base):
    """
    Row of data within a vendor catalog.
    """
    __tablename__ = 'vendor_catalog_row'
    __batch_class__ = VendorCatalog

    @declared_attr
    def __table_args__(cls):
        return cls.__default_table_args__() + (
            sa.ForeignKeyConstraint(['product_uuid'], ['product.uuid'],
                                    name='vendor_catalog_row_fk_product'),
            )

    STATUS_NO_CHANGE = 1
    STATUS_NEW_COST = 2
    STATUS_UPDATE_COST = 3
    STATUS_PRODUCT_NOT_FOUND = 4

    STATUS = {
        STATUS_NO_CHANGE:               "no change",
        STATUS_NEW_COST:                "new cost",
        STATUS_UPDATE_COST:             "cost update",
        STATUS_PRODUCT_NOT_FOUND:       "product not found",
        }

    upc = sa.Column(GPCType(), nullable=True, doc="""
    UPC for the row.
    """)

    product_uuid = sa.Column(sa.String(length=32), nullable=True)

    product = orm.relationship(
        Product, doc="""
        Reference to the :class:`Product` with which the row is associated, if any.
        """,
        backref=orm.backref('_vendor_catalog_rows', cascade='all'))

    vendor_code = sa.Column(sa.String(length=30), nullable=True, doc="""
    Vendor's unique code for the product.  The meaning of this corresponds to that
    of the :attr:`ProductCost.code` column.
    """)

    brand_name = sa.Column(sa.String(length=100), nullable=True, doc="""
    Brand name of the product.
    """)

    description = sa.Column(sa.String(length=255), nullable=False, default='', doc="""
    Description of the product.
    """)

    size = sa.Column(sa.String(length=255), nullable=True, doc="""
    Size of the product, as string.
    """)

    case_size = sa.Column(sa.Integer(), nullable=False, default=1, doc="""
    Number of units in a case of product.
    """)

    case_cost = sa.Column(sa.Numeric(precision=9, scale=5), nullable=True, doc="""
    Cost per case of the product.
    """)

    unit_cost = sa.Column(sa.Numeric(precision=9, scale=5), nullable=True, doc="""
    Cost per unit of the product.
    """)

    old_vendor_code = sa.Column(sa.String(length=30), nullable=True, doc="""
    Original vendor code for the product, if any.
    """)

    old_case_size = sa.Column(sa.Integer(), nullable=False, default=1, doc="""
    Original case size for the product, if any.
    """)

    old_case_cost = sa.Column(sa.Numeric(precision=9, scale=5), nullable=True, doc="""
    Original case cost for the product, if any.
    """)

    old_unit_cost = sa.Column(sa.Numeric(precision=9, scale=5), nullable=True, doc="""
    Original unit cost for the product, if any.
    """)

    case_cost_diff = sa.Column(sa.Numeric(precision=9, scale=5), nullable=True, doc="""
    Case cost difference between the catalog and product's original cost record.
    """)

    unit_cost_diff = sa.Column(sa.Numeric(precision=9, scale=5), nullable=True, doc="""
    Unit cost difference between the catalog and product's original cost record.
    """)
