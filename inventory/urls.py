from django.conf.urls import url

from views import *

urlpatterns = [
    # Inventory admin
    url(r'^add/$', inventoryAdd, name="add_inventory"),
    url(r'^delete/(\S+)/$', inventoryDelete, name="delete_inventory"),
    url(r'^edit/(\S+)/$', inventoryEdit, name="edit_inventory"),
    url(r'^list/$', inventoryList, name="list_inventory"),
    url(r'^listdeleted/(\S+)/$', inventoryList, name="list_deleted_inventory"),

    # Vendor
    url(r'^vendor/add/$', vendorAdd, name="add_vendor"),

    # Shipping/Recieving
    url(r'^receiving/$', receiveInventory, name="receive_inventory"),
    url(r'^shipping/$', shipInventory, name="ship_inventory"),

    # Reports
    url(r'^reports/total/$', reports, name="reports"),
    url(r'^history/$', showHistory, name="history"),
]