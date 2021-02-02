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
    vendor_name = models.ForeignKey(Vendor, on_delete=models.PROTECT)
    hidden = models.BooleanField()

    def __unicode__(self):
        return u'%s - %s | Quantity = %s' % (self.item_number, self.description, self.quantity)

    def grand_total(self):
        total = self.cost * self.quantity
        return total


class TransactionLog(models.Model):
    ENTRY_TYPE_CHOICES = (
        ('SHP', 'Shipped'),
        ('RCV', 'Received'),
        ('IAD', 'Added Item'),
        ('IDL', 'Deleted Item'),
        ('VAD', 'Added Vendor'),
        ('VDL', 'Deleted Vendor'),
    )

    entry_date = models.DateTimeField(auto_now_add=True)
    entry_type = models.CharField(max_length=3, choices=ENTRY_TYPE_CHOICES)
    entity_number = models.IntegerField(null=True, blank=True)
    entity_quantity = models.IntegerField(null=True, blank=True)

