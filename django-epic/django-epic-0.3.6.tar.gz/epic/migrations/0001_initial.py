# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from decimal import Decimal
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Assembly_Item',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('qty', models.PositiveIntegerField(help_text=b'The quantity of this component required by the assembly.')),
                ('refdes', models.TextField(default=b'', help_text=b'A list of comma-separated reference designators e.g., "R101,R304". The length of this list should match Quantity.', verbose_name=b'Refdes List', blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Delta',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('is_absolute', models.BooleanField(default=False, help_text=b'If set, the adjustment is absolute otherwise it is relative.', verbose_name=b'Absolute Adjustment')),
                ('adj', models.IntegerField(help_text=b'The amount by which the part quantity should be adjusted by.', verbose_name=b'Adjustment Count')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Line_Item',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('qty', models.PositiveIntegerField(help_text=b'The quantity of this part.')),
                ('line_cost', models.DecimalField(help_text=b'The total cost of this line-item.  Part-cost is line-item cost divided by quantity.', verbose_name=b'Amount', max_digits=9, decimal_places=2, validators=[django.core.validators.MinValueValidator(Decimal('0.00'))])),
                ('index', models.PositiveIntegerField(help_text=b'Sequential and unchanging index of this line-item.')),
            ],
            options={
                'ordering': ['index'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Part',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('val', models.CharField(default=b'', help_text=b'The primary value of the part such as resistance for a resistor or capacitance for a capacitor.', max_length=31, verbose_name=b'Value', blank=True)),
                ('descr', models.CharField(default=b'', help_text=b'Brief listing of key parameters of the part, such as temperature range, drift, max. voltages, etc.', max_length=127, verbose_name=b'Description', blank=True)),
                ('footprint', models.CharField(default=b'', help_text=b"The part's PCB footprint.", max_length=63, blank=True)),
                ('mfg', models.CharField(help_text=b'The name of the manufacturer of the part.', max_length=31, verbose_name=b'Manufacturer')),
                ('mfg_pn', models.CharField(max_length=31, verbose_name=b"Manufacturer's Part #")),
                ('mounting', models.IntegerField(default=0, help_text=b"How the part is mounted to a PCB (free if it's not mounted at all, such as a plug).", verbose_name=b'Mounting Type', choices=[(0, b'SMD'), (1, b'THD'), (2, b'chassis'), (3, b'free')])),
                ('target_price', models.DecimalField(help_text=b'The expected price of the part.', verbose_name=b'Target price [$]', max_digits=10, decimal_places=6, validators=[django.core.validators.MinValueValidator(Decimal('0.000001'))])),
                ('overage', models.DecimalField(help_text=b'Worst-case percentage of parts we expect to lose due to attrition at the assembly-house.', verbose_name=b'Overage [%]', max_digits=6, decimal_places=3, validators=[django.core.validators.MinValueValidator(Decimal('0')), django.core.validators.MaxValueValidator(Decimal('100'))])),
                ('spq', models.IntegerField(default=1, help_text=b'The number of parts in a standard package.  For example, 10,000 pieces in a reel.', verbose_name=b'Standard-Package Qty')),
                ('lead_time', models.PositiveIntegerField(help_text=b'Lead-time in weeks.', verbose_name=b'Lead-time [weeks]')),
                ('status', models.IntegerField(default=0, help_text=b"The life-time status of this part. Parts marked `preview' and `obsolete' are not considered orderable.", verbose_name=b'Life-time Status', choices=[(0, b'preview'), (1, b'active'), (2, b'deprecated'), (3, b'obsolete')])),
                ('substitute', models.ForeignKey(blank=True, to='epic.Part', help_text=b'List of other parts that are (identical) substitutes for this part.', null=True, verbose_name=b'Substitutes')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ts', models.DateTimeField(help_text=b'Date and time when this transaction was created.', verbose_name=b'Creation Time')),
                ('notes', models.TextField(help_text=b'Comments and notes for this transaction', verbose_name=b'Notes', blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Shipment',
            fields=[
                ('transaction_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='epic.Transaction')),
                ('tracking', models.CharField(default=b'', help_text=b'Comma-separated list of tracking numbers.', max_length=127, verbose_name=b'Tracking #s', blank=True)),
                ('cost_freight', models.DecimalField(verbose_name=b'Freight Cost', max_digits=9, decimal_places=2, validators=[django.core.validators.MinValueValidator(Decimal('0.00'))])),
                ('cost_other', models.DecimalField(help_text=b'Other costs assessed by the shipper, such as handling costs.', verbose_name=b'Other Costs', max_digits=9, decimal_places=2, validators=[django.core.validators.MinValueValidator(Decimal('0.00'))])),
                ('cost_discount', models.DecimalField(help_text=b'Discounts given by the shipper, such as early payment discount.', verbose_name=b'Discount Given', max_digits=9, decimal_places=2, validators=[django.core.validators.MinValueValidator(Decimal('0.00'))])),
            ],
            options={
            },
            bases=('epic.transaction',),
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('transaction_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='epic.Transaction')),
                ('expected_arrival_date', models.DateField(help_text=b'Date when the order is expected to arrive.', verbose_name=b'Expected Arrival Date')),
                ('status', models.IntegerField(default=0, verbose_name=b'Order Status', choices=[(0, b'open'), (1, b'closed')])),
            ],
            options={
            },
            bases=('epic.transaction',),
        ),
        migrations.CreateModel(
            name='Inventory',
            fields=[
                ('transaction_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='epic.Transaction')),
            ],
            options={
            },
            bases=('epic.transaction',),
        ),
        migrations.CreateModel(
            name='Vendor',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=31, verbose_name=b'Vendor Name', db_index=True)),
                ('search_url', models.CharField(default=b'', help_text=b"This pattern defines how to search for a particular part on the vendor's website.  %(vendor_pn)s gets replaced by the vendor's part-number, %(mfg)s by the manufacturer's name, and %(mfg_pn)s by the manufacturer's part-number.", max_length=127, verbose_name=b'Search URL Pattern', blank=True)),
            ],
            options={
                'ordering': ['name'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Vendor_Part',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('vendor_pn', models.CharField(max_length=31, verbose_name=b"Vendor's Part #")),
                ('price', models.DecimalField(max_digits=10, decimal_places=6, validators=[django.core.validators.MinValueValidator(Decimal('0.000001'))])),
                ('part', models.ForeignKey(verbose_name=b'Part #', to='epic.Part')),
                ('vendor', models.ForeignKey(to='epic.Vendor')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Warehouse',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text=b'The name of the warehouse.', unique=True, max_length=31)),
                ('address', models.TextField(default=b'', help_text=b'The shipping address for the warehouse.', blank=True)),
            ],
            options={
                'ordering': ['name'],
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='vendor_part',
            unique_together=set([('vendor', 'vendor_pn'), ('vendor', 'part')]),
        ),
        migrations.AddField(
            model_name='transaction',
            name='warehouse',
            field=models.ForeignKey(verbose_name=b'Warehouse', to='epic.Warehouse', help_text=b'The (destination) warehouse this transaction applies to.'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='shipment',
            name='from_warehouse',
            field=models.ForeignKey(blank=True, to='epic.Warehouse', help_text=b'For an inter-warehouse shipment, the warehouse the shipment originates from.', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='shipment',
            name='ordr',
            field=models.ForeignKey(blank=True, to='epic.Order', help_text=b'For an order shipment, the order that resulted in this shipment.', null=True, verbose_name=b'Order #'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='part',
            unique_together=set([('mfg', 'mfg_pn')]),
        ),
        migrations.AlterIndexTogether(
            name='part',
            index_together=set([('mfg', 'mfg_pn')]),
        ),
        migrations.AddField(
            model_name='order',
            name='vendor',
            field=models.ForeignKey(help_text=b'The name of the vendor (distributor) where the order was placed.', to='epic.Vendor'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='line_item',
            name='part',
            field=models.ForeignKey(verbose_name=b'Part #', to='epic.Part'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='line_item',
            name='txtn',
            field=models.ForeignKey(verbose_name=b'Transaction #', to='epic.Transaction'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='line_item',
            unique_together=set([('txtn', 'part'), ('txtn', 'index')]),
        ),
        migrations.AlterIndexTogether(
            name='line_item',
            index_together=set([('txtn', 'part')]),
        ),
        migrations.AddField(
            model_name='delta',
            name='part',
            field=models.ForeignKey(verbose_name=b'Part #', to='epic.Part', help_text=b'The part whose quantity gets adjusted.'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='delta',
            name='txtn',
            field=models.ForeignKey(verbose_name=b'Transaction #', to='epic.Transaction'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='delta',
            name='warehouse',
            field=models.ForeignKey(to='epic.Warehouse'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='assembly_item',
            name='assy',
            field=models.ForeignKey(related_name='assembly_item_part', verbose_name=b'Assembly Part #', to='epic.Part', help_text=b'The part number of the assembly this item belongs to.'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='assembly_item',
            name='comp',
            field=models.ForeignKey(related_name='assembly_item_comp', verbose_name=b'Component Part #', to='epic.Part', help_text=b'The part number of the component of this item.'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='assembly_item',
            unique_together=set([('assy', 'comp')]),
        ),
        migrations.AlterIndexTogether(
            name='assembly_item',
            index_together=set([('assy', 'comp')]),
        ),
    ]
