from django.utils.safestring import mark_safe
from django.forms import Form,BooleanField,CharField,DecimalField,IntegerField,ModelChoiceField

from .models import *

class InventoryForm(Form):

    itemnumber  = CharField()
    description = CharField()
    vendor      = ModelChoiceField(queryset=Vendor.objects.all().order_by('vendor_name'), empty_label=None)
    quantity    = CharField()
    cost        = CharField()
    hidden      = BooleanField(required=False)

    #def clean_cost(self):
    #    cost = self.cleaned_data['cost']


class VendorForm(Form):

    name = CharField()


class QuantityForm(Form):
    item = ModelChoiceField(queryset=Item.objects.all().order_by("item_number").exclude(hidden=1), empty_label=None)
    quantity = IntegerField()

