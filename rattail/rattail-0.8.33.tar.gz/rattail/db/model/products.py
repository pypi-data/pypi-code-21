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
Data Models for Products
"""

from __future__ import unicode_literals, absolute_import

import datetime

import six
import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy.ext.orderinglist import ordering_list
from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy.ext.associationproxy import association_proxy

from rattail import enum
from rattail.db.model import (Base, uuid_column, getset_factory,
                              Department, Subdepartment, Category, Vendor, Store)
from rattail.db.types import GPCType
from rattail.db.util import make_full_description
from rattail.util import pretty_quantity


@six.python_2_unicode_compatible
class Brand(Base):
    """
    Represents a brand or similar product line.
    """
    __tablename__ = 'brand'
    __versioned__ = {}

    uuid = uuid_column()
    name = sa.Column(sa.String(length=100), nullable=True)

    def __str__(self):
        return self.name or ''


@six.python_2_unicode_compatible
class Tax(Base):
    """
    Represents a sales tax rate to be applied to products.
    """
    __tablename__ = 'tax'
    __table_args__ = (
        sa.UniqueConstraint('code', name='tax_uq_code'),
    )
    __versioned__ = {}

    uuid = uuid_column()

    code = sa.Column(sa.String(length=30), nullable=False, doc="""
    Unique "code" for the tax rate.
    """)

    description = sa.Column(sa.String(length=255), nullable=True, doc="""
    Human-friendly description for the tax rate.
    """)

    rate = sa.Column(sa.Numeric(precision=7, scale=5), nullable=False, doc="""
    Percentage rate for the tax, e.g. 8.25.
    """)

    def __str__(self):
        if self.description:
            return self.description
        return "{} ({}%)".format(self.code, pretty_quantity(self.rate))


class Product(Base):
    """
    Represents a product for sale and/or purchase.
    """
    __tablename__ = 'product'
    __table_args__ = (
        sa.ForeignKeyConstraint(['unit_uuid'], ['product.uuid'], name='product_fk_unit'),
        sa.ForeignKeyConstraint(['department_uuid'], ['department.uuid'], name='product_fk_department'),
        sa.ForeignKeyConstraint(['subdepartment_uuid'], ['subdepartment.uuid'], name='product_fk_subdepartment'),
        sa.ForeignKeyConstraint(['category_uuid'], ['category.uuid'], name='product_fk_category'),
        sa.ForeignKeyConstraint(['family_uuid'], ['family.uuid'], name='product_fk_family'),
        sa.ForeignKeyConstraint(['brand_uuid'], ['brand.uuid'], name='product_fk_brand'),
        sa.ForeignKeyConstraint(['report_code_uuid'], ['report_code.uuid'], name='product_fk_report_code'),
        sa.ForeignKeyConstraint(['deposit_link_uuid'], ['deposit_link.uuid'], name='product_fk_deposit_link'),
        sa.ForeignKeyConstraint(['tax_uuid'], ['tax.uuid'], name='product_fk_tax'),
        sa.ForeignKeyConstraint(['regular_price_uuid'], ['product_price.uuid'], name='product_fk_regular_price', use_alter=True),
        sa.ForeignKeyConstraint(['current_price_uuid'], ['product_price.uuid'], name='product_fk_current_price', use_alter=True),
        sa.Index('product_ix_upc', 'upc'),
    )
    __versioned__ = {'exclude': ['last_sold']}

    uuid = uuid_column()

    upc = sa.Column(GPCType(), nullable=True, doc="""
    Proper GPC value for the product, if any.
    """)

    scancode = sa.Column(sa.String(length=14), nullable=True, doc="""
    Scan code (as string) for the product, if any.  This is generally intended
    to match the :attr:`upc` value, though that is not enforced.
    """)

    item_id = sa.Column(sa.String(length=20), nullable=True, doc="""
    Generic ID string for the item.
    """)

    item_type = sa.Column(sa.Integer(), nullable=True, doc="""
    Item type code as integer.
    """)

    department_uuid = sa.Column(sa.String(length=32))
    subdepartment_uuid = sa.Column(sa.String(length=32))
    category_uuid = sa.Column(sa.String(length=32))
    family_uuid = sa.Column(sa.String(length=32))

    report_code_uuid = sa.Column(sa.String(length=32), nullable=True, doc="""
    UUID of the product's report code, if any.
    """)

    deposit_link_uuid = sa.Column(sa.String(length=32), nullable=True, doc="""
    UUID of the product's deposit link, if any.
    """)

    deposit_link = orm.relationship('DepositLink', doc="""
    Reference to the :class:`DepositLink` instance with which the product
    associates, if any.
    """)

    tax_uuid = sa.Column(sa.String(length=32), nullable=True, doc="""
    UUID of the product's tax, if any.
    """)

    tax = orm.relationship(Tax, doc="""
    Reference to the :class:`Tax` instance with which the product associates, if
    any.
    """)

    brand_uuid = sa.Column(sa.String(length=32))

    description = sa.Column(sa.String(length=255), nullable=True, doc="""
    Primary description for the item.
    """)

    description2 = sa.Column(sa.String(length=255), nullable=True, doc="""
    Secondary description for the item.
    """)

    size = sa.Column(sa.String(length=30), nullable=True, doc="""
    Free-form / human-friendly size string for the product, e.g. '32 oz'
    """)

    unit_size = sa.Column(sa.Numeric(precision=8, scale=3), nullable=True, doc="""
    Unit size for product, as decimal.  This refers to the numeric size of a unit
    of the product, in terms of the :attr:`unit_of_measure`, and may be used for
    smarter price comparisons etc.
    """)

    unit_of_measure = sa.Column(sa.String(length=4), nullable=False,
                                default=enum.UNIT_OF_MEASURE_NONE, doc="""
    Code indicating the unit of measure for the product.  Value should be one of
    the keys of the ``rattail.enum.UNIT_OF_MEASURE`` dictionary.
    """)

    uom_abbreviation = sa.Column(sa.String(length=4), nullable=True, doc="""
    Optional abbreviated unit of measure.  This value is intended to contain a
    human-friendly abbreviation for the :attr:`unit_of_measure`.  This value is
    generally also seen at the end of :attr:`size`.
    """)

    weighed = sa.Column(sa.Boolean(), nullable=False, default=False, doc="""
    Whether or not the product must be weighed to determine its final price.
    """)

    unit_uuid = sa.Column(sa.String(length=32), nullable=True)

    unit = orm.relationship(
        'Product',
        remote_side=[uuid],
        doc="""
        Reference to the *unit* product upon which this product is based, if any.
        """,
        backref=orm.backref(
            'packs',
            doc="""
            List of products which reference the current product as their unit.
            """))

    pack_size = sa.Column(sa.Numeric(precision=9, scale=4), nullable=True, doc="""
    Number of *units* which constitute the current *pack* product, if applicable.
    """)

    case_size = sa.Column(sa.Numeric(precision=9, scale=4), nullable=True, doc="""
    Case size for the product, i.e. how many units (current product) are
    included when *sold* as a case.
    """)

    organic = sa.Column(sa.Boolean(), nullable=False, default=False, doc="""
    Whether the item is organic.
    """)

    kosher = sa.Column(sa.Boolean(), nullable=True, doc="""
    Whether the item is kosher.
    """)

    vegan = sa.Column(sa.Boolean(), nullable=True, doc="""
    Whether the item is vegan.
    """)

    vegetarian = sa.Column(sa.Boolean(), nullable=True, doc="""
    Whether the item is vegetarian.
    """)

    gluten_free = sa.Column(sa.Boolean(), nullable=True, doc="""
    Whether the item is gluten-free.
    """)

    sugar_free = sa.Column(sa.Boolean(), nullable=True, doc="""
    Whether the item is sugar-free.
    """)

    not_for_sale = sa.Column(sa.Boolean(), nullable=False, default=False, doc="""
    Flag to indicate items which are not available for sale.
    """)

    discontinued = sa.Column(sa.Boolean(), nullable=False, default=False, doc="""
    Flag to indicate an item has been discontinued.
    """)

    deleted = sa.Column(sa.Boolean(), nullable=False, default=False, doc="""
    Flag to indicate items which have been deleted.  Obviously this is implies
    "false" deletion, where the record is actually kept on file.  Whether or not
    you use this is up to you.
    """)

    regular_price_uuid = sa.Column(sa.String(length=32))
    current_price_uuid = sa.Column(sa.String(length=32))

    discountable = sa.Column(sa.Boolean(), nullable=False, default=True, doc="""
    Whether or not the product may be discounted in any way.
    """)

    special_order = sa.Column(sa.Boolean(), nullable=False, default=False, doc="""
    Whether the product is available for special order.
    """)

    food_stampable = sa.Column(sa.Boolean(), nullable=True, doc="""
    Flag indicating whether food stamps are a valid form of payment for the item.
    """)

    tax1 = sa.Column(sa.Boolean(), nullable=True, doc="""
    (hack?) Flag indicating whether 'tax 1' applies to the item.
    """)

    tax2 = sa.Column(sa.Boolean(), nullable=True, doc="""
    (hack?) Flag indicating whether 'tax 2' applies to the item.
    """)

    tax3 = sa.Column(sa.Boolean(), nullable=True, doc="""
    (hack?) Flag indicating whether 'tax 3' applies to the item.
    """)

    last_sold = sa.Column(sa.DateTime(), nullable=True, doc="""
    UTC timestamp of the product's last sale event.
    """)

    ingredients = sa.Column(sa.Text(), nullable=True, doc="""
    Free-form ingredients for the product.
    """)

    status_code = sa.Column(sa.Integer(), nullable=True, doc="""
    Status code for the product.  Interpretation of this value is left to the
    custom app logic.
    """)

    notes = sa.Column(sa.Text(), nullable=True, doc="""
    Generic / free-form notes for the product.
    """)

    department = orm.relationship(Department, order_by=Department.name)

    subdepartment = orm.relationship(
        Subdepartment,
        order_by=Subdepartment.name,
        backref=orm.backref('products'))

    category = orm.relationship(
        Category,
        backref=orm.backref('products'))

    brand = orm.relationship(Brand)

    family = orm.relationship(
        'Family',
        doc="""
        Reference to the :class:`Family` instance with which the product
        associates, if any.
        """,
        backref=orm.backref(
            'products',
            doc="""
            List of :class:`Product` objects which belong to this family.
            """))

    report_code = orm.relationship(
        'ReportCode',
        doc="""
        Reference to the :class:`ReportCode` instance with which the product
        associates, if any.
        """,
        backref=orm.backref(
            'products',
            doc="""
            List of :class:`Product` objects which associate with this report code.
            """))

    def __str__(self):
        if six.PY2:
            return self.full_description.encode('utf8')
        return self.full_description

    if six.PY2:
        def __unicode__(self):
            return self.full_description

    @property
    def full_description(self):
        """
        Convenience attribute which returns a more complete description.

        Most notably, this includes the brand name and product size.
        """
        return make_full_description(self.brand.name if self.brand else '',
                                     self.description, self.size)

    @property
    def pretty_upc(self):
        """
        Product's UPC as a somewhat human-readable string.
        """
        if self.upc is None:
            return None
        return self.upc.pretty()

    def cost_for_vendor(self, vendor):
        """
        Of the product's cost records, return the first one associated with the
        given vendor.
        """
        for cost in self.costs:
            if cost.vendor is vendor:
                return cost


class ProductImage(Base):
    """
    Contains an image for a product.
    """
    __tablename__ = 'product_image'
    __table_args__ = (
        sa.ForeignKeyConstraint(['product_uuid'], ['product.uuid'], name='product_image_fk_product'),
    )

    uuid = uuid_column()

    product_uuid = sa.Column(sa.String(length=32), nullable=False)
    product = orm.relationship(
        Product,
        doc="""
        Reference to the product which is shown by the image.
        """,
        backref=orm.backref(
            'image',
            uselist=False,
            doc="""
            Reference to the product's image, if any.
            """))

    bytes = sa.Column(sa.LargeBinary(), nullable=False)


@six.python_2_unicode_compatible
class ProductCode(Base):
    """
    Represents an arbitrary "code" for a product.
    """
    __tablename__ = 'product_code'
    __table_args__ = (
        sa.ForeignKeyConstraint(['product_uuid'], ['product.uuid'], name='product_code_fk_product'),
        )
    __versioned__ = {}

    uuid = uuid_column()
    product_uuid = sa.Column(sa.String(length=32), nullable=False)
    ordinal = sa.Column(sa.Integer(), nullable=False)
    code = sa.Column(sa.String(length=20), nullable=True)

    def __str__(self):
        return self.code or ''


Product._codes = orm.relationship(
    ProductCode, backref='product',
    collection_class=ordering_list('ordinal', count_from=1),
    order_by=ProductCode.ordinal,
    cascade='save-update, merge, delete, delete-orphan')

Product.codes = association_proxy(
    '_codes', 'code',
    getset_factory=getset_factory,
    creator=lambda c: ProductCode(code=c))

Product._code = orm.relationship(
    ProductCode,
    primaryjoin=sa.and_(
        ProductCode.product_uuid == Product.uuid,
        ProductCode.ordinal == 1,
        ),
    uselist=False,
    viewonly=True)

Product.code = association_proxy(
    '_code', 'code',
    getset_factory=getset_factory)


class ProductCost(Base):
    """
    Represents a source from which a product may be obtained via purchase.
    """
    __tablename__ = 'product_cost'
    __table_args__ = (
        sa.ForeignKeyConstraint(['product_uuid'], ['product.uuid'], name='product_cost_fk_product'),
        sa.ForeignKeyConstraint(['vendor_uuid'], ['vendor.uuid'], name='product_cost_fk_vendor'),
        )
    __versioned__ = {}

    uuid = uuid_column()
    product_uuid = sa.Column(sa.String(length=32), nullable=False)
    vendor_uuid = sa.Column(sa.String(length=32), nullable=False)
    preference = sa.Column(sa.Integer(), nullable=False)
    code = sa.Column(sa.String(length=20))

    case_size = sa.Column(sa.Numeric(precision=9, scale=4), nullable=True, doc="""
    Number of units which constitute a "case" in the context of this vendor
    catalog item.  May be a fractional quantity, e.g. 17.5LB.
    """)

    case_cost = sa.Column(sa.Numeric(precision=9, scale=5))
    pack_size = sa.Column(sa.Integer())
    pack_cost = sa.Column(sa.Numeric(precision=9, scale=5))
    unit_cost = sa.Column(sa.Numeric(precision=9, scale=5))
    effective = sa.Column(sa.DateTime())

    discontinued = sa.Column(sa.Boolean(), nullable=True, doc="""
    Flag to indicate if the cost record has been discontinued, presumably by
    the vendor.
    """)

    vendor = orm.relationship(
        Vendor,
        backref=orm.backref('product_costs', cascade='all'))


Product.costs = orm.relationship(
    ProductCost, backref='product',
    collection_class=ordering_list('preference', count_from=1),
    order_by=ProductCost.preference,
    cascade='save-update, merge, delete, delete-orphan')

Product.cost = orm.relationship(
    ProductCost,
    primaryjoin=sa.and_(
        ProductCost.product_uuid == Product.uuid,
        ProductCost.preference == 1,
        ),
    uselist=False,
    viewonly=True)

Product.vendor = orm.relationship(
    Vendor,
    secondary=ProductCost.__table__,
    primaryjoin=sa.and_(
        ProductCost.product_uuid == Product.uuid,
        ProductCost.preference == 1,
        ),
    secondaryjoin=Vendor.uuid == ProductCost.vendor_uuid,
    uselist=False,
    viewonly=True)


class ProductPrice(Base):
    """
    Represents a price for a product.
    """
    __tablename__ = 'product_price'
    __table_args__ = (
        sa.ForeignKeyConstraint(['product_uuid'], ['product.uuid'], name='product_price_fk_product'),
        )
    __versioned__ = {}

    uuid = uuid_column()
    product_uuid = sa.Column(sa.String(length=32), nullable=False)
    type = sa.Column(sa.Integer())
    level = sa.Column(sa.Integer())
    starts = sa.Column(sa.DateTime())
    ends = sa.Column(sa.DateTime())
    price = sa.Column(sa.Numeric(precision=8, scale=3))
    multiple = sa.Column(sa.Integer())
    pack_price = sa.Column(sa.Numeric(precision=8, scale=3))
    pack_multiple = sa.Column(sa.Integer())

    def active_now(self):
        """
        Returns boolean indicating whether the price is currently active,
        i.e. "now" falls within time window defined by :attr:`starts` and
        :attr:`ends`.  Note that if the price has no start and/or end time,
        this will return ``True``.
        """
        now = datetime.datetime.utcnow()
        if self.starts and self.ends:
            return self.starts <= now <= self.ends
        elif self.starts:
            return self.starts <= now
        elif self.ends:
            return now <= self.ends
        return True


Product.prices = orm.relationship(
    ProductPrice, backref='product',
    primaryjoin=ProductPrice.product_uuid == Product.uuid,
    cascade='save-update, merge, delete, delete-orphan')

Product.regular_price = orm.relationship(
    ProductPrice,
    primaryjoin=Product.regular_price_uuid == ProductPrice.uuid,
    lazy='joined',
    post_update=True)

Product.current_price = orm.relationship(
    ProductPrice,
    primaryjoin=Product.current_price_uuid == ProductPrice.uuid,
    lazy='joined',
    post_update=True)


class ProductInventory(Base):
    """
    Inventory data for a product.  Assumption at this point is that this data
    will be accurate only in the context of the "local" node (store etc.).
    Tracking inventory for multiple nodes is not yet supported in the "host"
    sense; however each node may track its own inventory (only).
    """
    __tablename__ = 'product_inventory'
    __table_args__ = (
        sa.ForeignKeyConstraint(['product_uuid'], ['product.uuid'], name='product_inventory_fk_product'),
    )

    uuid = uuid_column()

    product_uuid = sa.Column(sa.String(length=32), nullable=False)
    product = orm.relationship(
        Product,
        doc="""
        Product to which this inventory record pertains.
        """,
        backref=orm.backref(
            'inventory',
            uselist=False,
            doc="""
            Inventory data for the product, if any.
            """))

    on_hand = sa.Column(sa.Numeric(precision=9, scale=4), nullable=True, doc="""
    Unit quantity of product which is currently on hand.
    """)

    on_order = sa.Column(sa.Numeric(precision=9, scale=4), nullable=True, doc="""
    Unit quantity of product which is currently on order.
    """)


class ProductStoreInfo(Base):
    """
    General store-specific info for a product.
    """
    __tablename__ = 'product_store_info'
    __table_args__ = (
        sa.ForeignKeyConstraint(['product_uuid'], ['product.uuid'], name='product_store_info_fk_product'),
        sa.ForeignKeyConstraint(['store_uuid'], ['store.uuid'], name='product_store_info_fk_store'),
    )

    uuid = uuid_column()

    product_uuid = sa.Column(sa.String(length=32), nullable=False)
    product = orm.relationship(
        Product,
        doc="""
        Product to which this info record pertains.
        """,
        backref=orm.backref(
            'store_infos',
            collection_class=attribute_mapped_collection('store_uuid'),
            doc="""
            List of store-specific info records for the product.
            """))

    store_uuid = sa.Column(sa.String(length=32), nullable=False)
    store = orm.relationship(
        Store,
        doc="""
        Store to which this info record pertains.
        """)

    recently_active = sa.Column(sa.Boolean(), nullable=True, doc="""
    Flag indicating the product has seen "recent activity" at the store.  How
    this is populated and/or interpreted is up to custom app logic.
    """)
