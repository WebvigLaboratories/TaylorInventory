from django.contrib import admin
from .models import Vendor, Item, TransactionLog

class VendorAdmin(admin.ModelAdmin):
    list_display = ('vendor_name',)
    search_fields = ('vendor_name',)
    ordering = ('vendor_name',)

class ItemAdmin(admin.ModelAdmin):
    list_display = ('item_number', 'description')
    search_fields = ('item_number', 'description')
    ordering = ('item_number',)

admin.site.register(Vendor, VendorAdmin)
admin.site.register(Item, ItemAdmin)
admin.site.register(TransactionLog)