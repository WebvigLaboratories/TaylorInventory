# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('item_number', models.CharField(max_length=30)),
                ('description', models.CharField(max_length=30, verbose_name=b'Item Name')),
                ('cost', models.DecimalField(max_digits=7, decimal_places=2)),
                ('quantity', models.IntegerField()),
                ('hidden', models.BooleanField()),
            ],
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateField()),
                ('type', models.CharField(max_length=10)),
                ('item_number', models.ForeignKey(to='inventory.Item')),
            ],
        ),
        migrations.CreateModel(
            name='Vendor',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('vendor_name', models.CharField(max_length=30)),
            ],
        ),
        migrations.AddField(
            model_name='item',
            name='vendor_name',
            field=models.ForeignKey(to='inventory.Vendor'),
        ),
    ]
