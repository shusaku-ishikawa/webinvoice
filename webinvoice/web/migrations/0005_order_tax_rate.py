# Generated by Django 2.1.5 on 2019-03-17 11:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0004_invoice_due_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='tax_rate',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='web.TaxRate', verbose_name='税率'),
        ),
    ]
