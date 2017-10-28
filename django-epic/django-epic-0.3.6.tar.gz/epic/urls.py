#
#   Copyright (c) 2014-2016 eGauge Systems LLC
# 	4730 Walnut St, Suite 110
# 	Boulder, CO 80301
# 	voice: 720-545-9767
# 	email: davidm@egauge.net
#
#   All rights reserved.
#
#   This code is the property of eGauge Systems LLC and may not be
#   copied, modified, or disclosed without any prior and written
#   permission from eGauge Systems LLC.
#
from django.conf.urls import include, url

from epic import exports
from epic import views
from epic import perms

urlpatterns = [
    url(r'^$', views.epic_index, name='epic_index'),
    url(r'^search-results$', views.search_results, name='search_results'),

    url(r'^part/$', views.part_list, name='part_list'),
    url(r'^part/add$', views.part_add, name='part_add'),
    url(r'^part/info$', views.part_info, name='part_info'),
    url(r'^part/(?P<pk>\d+)/$', views.part_detail, name='part_detail'),
    url(r'^part/(?P<pk>\d+)/edit$', views.part_edit, name='part_edit'),
    url(r'^part/(?P<pk>\d+)/delete$', views.part_delete, name='part_delete'),
    url(r'^part/(?P<pk>\d+)/bom$', views.part_bom_detail,
        name='part_bom_detail'),
    url(r'^part/(?P<pk>\d+)/bom/edit$', views.part_bom_edit,
        name='part_bom_edit'),
    url(r'^part/(?P<pk>\d+)/bom/export$', exports.part_bom_export,
        name='part_bom_export'),
    url(r'^part/datasheet/$', views.datasheet_list, name='datasheet_list'),
    url(r'^part/datasheet/add$', views.datasheet_add,
        name='datasheet_add'),
    url(r'^part/datasheet/add/(?P<pk>\d+)$', views.datasheet_add_part,
        name='datasheet_add_part'),
    url(r'^part/datasheet/(?P<pk>\d+)/$', views.datasheet_detail,
        name='datasheet_detail'),
    url(r'^part/datasheet/(?P<pk>\d+)/edit$',
        views.datasheet_edit, name='datasheet_edit'),
    url(r'^part/datasheet/(?P<pk>\d+)/delete$', views.datasheet_delete,
        name='datasheet_delete'),

    url(r'^vendor/$', views.vendor_list, name='vendor_list'),
    url(r'^vendor/add$', views.vendor_add, name='vendor_add'),
    url(r'^vendor/(?P<pk>\d+)/$', views.vendor_detail, name='vendor_detail'),
    url(r'^vendor/(?P<pk>\d+)/edit$', views.vendor_edit, name='vendor_edit'),
    url(r'^vendor/(?P<pk>\d+)/delete$', views.vendor_delete,
        name='vendor_delete'),

    url(r'^warehouse/$', views.warehouse_list, name='warehouse_list'),
    url(r'^warehouse/stock$', views.warehouse_stock_all,
        name='warehouse_stock_all'),
    url(r'^warehouse/stock/export$', exports.warehouse_stock_all_export,
        name='warehouse_stock_all_export'),
    url(r'^warehouse/add$', views.warehouse_add, name='warehouse_add'),
    url(r'^warehouse/(?P<pk>\d+)/$', views.warehouse_detail,
        name='warehouse_detail'),
    # this is simply an alias since the warehouse_detail already lists
    # the inventories associated with that warehouse:
    url(r'^warehouse/(?P<pk>\d+)/inventory$',
        views.warehouse_inventory, name='warehouse_inventory'),
    url(r'^warehouse/(?P<pk>\d+)/edit$', views.warehouse_edit,
        name='warehouse_edit'),
    url(r'^warehouse/(?P<pk>\d+)/add-shipment$', views.warehouse_add_shipment,
        name='warehouse_add_shipment'),
    url(r'^warehouse/(?P<pk>\d+)/add-inventory$',
        views.warehouse_add_inventory, name='warehouse_add_inventory'),
    url(r'^warehouse/(?P<pk>\d+)/stock$', views.warehouse_stock,
        name='warehouse_stock'),
    url(r'^warehouse/(?P<pk>\d+)/stock/export$', exports.warehouse_stock_export,
        name='warehouse_stock_export'),
    url(r'^warehouse/(?P<pk>\d+)/delete$', views.warehouse_delete,
        name='warehouse_delete'),
    url(r'^warehouse/(?P<warehouse>\d+)/inventory/(?P<pk>\d+)$',
        views.warehouse_inv_detail, name='warehouse_inventory_detail'),
    url(r'^warehouse/(?P<warehouse>\d+)/inventory/(?P<pk>\d+)/export$',
        exports.warehouse_inv_export, name='warehouse_inventory_export'),
    url(r'^warehouse/(?P<warehouse>\d+)/inventory/(?P<pk>\d+)/edit$',
        views.inventory_edit, name='warehouse_inventory_edit'),
    url(r'^warehouse/(?P<warehouse>\d+)/inventory/(?P<pk>\d+)/delete$',
        views.inventory_delete, name='warehouse_inventory_delete'),

    url(r'^order/$', views.order_list, name='order_list'),
    url(r'^order/add$', views.order_add, name='order_add'),
    url(r'^order/(?P<pk>\d+)/$', views.order_detail, name='order_detail'),
    url(r'^order/(?P<pk>\d+)/export$', exports.order_export,
        name='order_export'),
    url(r'^order/(?P<pk>\d+)/edit$', views.order_edit, name='order_edit'),
    url(r'^order/(?P<pk>\d+)/check-stock$', views.order_check_stock,
        name='order_check_stock'),
    url(r'^order/(?P<pk>\d+)/add-shipment$', views.order_add_shipment,
        name='order_add_shipment'),
    url(r'^order/(?P<pk>\d+)/delete$', views.order_delete, name='order_delete'),

    url(r'^ship/$', views.ship_list, name='ship_list'),
    url(r'^ship/add$', views.ship_add, name='ship_add'),
    url(r'^ship/(?P<pk>\d+)/$', views.ship_detail, name='ship_detail'),
    url(r'^ship/(?P<pk>\d+)/export$', exports.ship_export, name='ship_export'),
    url(r'^ship/(?P<pk>\d+)/edit$', views.ship_edit, name='ship_edit'),
    url(r'^ship/(?P<pk>\d+)/delete$', views.ship_delete, name='ship_delete'),

    url(r'^dal/part/$', views.Part_Autocomplete.as_view(), name='part-dal'),
    url(r'^dal/order/$', views.Order_Autocomplete.as_view(), name='order-dal'),
    url(r'^dal/mfg/$', views.Mfg_Autocomplete.as_view(), name='mfg-dal'),
    url(r'^dal/footprint/$', views.Footprint_Autocomplete.as_view(),
        name='footprint-dal'),]
