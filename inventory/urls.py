from __future__ import unicode_literals

from django.conf.urls import url
from django.views.generic import TemplateView

from .views import *

urlpatterns = [
    url(r'^$', index, name='home'),

    # Inventory admin
    url(r'^add/$', inventory_add, name="add_inventory"),
    url(r'^delete/(\S+)/$', inventory_delete, name="delete_inventory"),
    url(r'^edit/(\S+)/$', inventory_edit, name="edit_inventory"),
    url(r'^list/$', inventory_list, name="list_inventory"),
    url(r'^listdeleted/(\S+)/$', inventory_list, name="list_deleted_inventory"),

    # Vendor
    url(r'^vendor/add/$', vendor_add, name="add_vendor"),

    # Shipping/Recieving
    url(r'^receiving/$', receive_inventory, name="receive_inventory"),
    url(r'^shipping/$', ship_inventory, name="ship_inventory"),

    # Reports
    url(r'^reports/inventoryfinancial/$', report_full_inventory, name="inventory_financial"),
    url(r'^reports/transactiondaily/(\S+)/$', report_daily_transactions, name="daily_transaction_report"),
    url(r'^reports/transactioncustom/$', TemplateView.as_view(template_name='reports/select_date_range.html'),
        name="custom_transaction_report"),
]
