from django.db import models

class Vendor(models.Model):
    vendor_name = models.CharField(max_length=30)

    def __unicode__(self):
        return self.vendor_name

class Item(models.Model):
    item_number = models.CharField(max_length=30)
    description = models.CharField(max_length=30, verbose_name='Item Name')
    cost = models.DecimalField(max_digits=7, decimal_places=2)
    quantity = models.IntegerField()
    vendor_name = models.ForeignKey(Vendor)
    hidden = models.BooleanField()

    def __unicode__(self):
        return u'%s - %s | Quantity = %s' % (self.item_number, self.description, self.quantity)

    def grand_total(self):
        total = self.cost * self.quantity
        return total

class Transaction(models.Model):
    date = models.DateField()
    type = models.CharField(max_length=10)
    item_number = models.ForeignKey(Item)

