# Generated by Django 2.1.5 on 2019-04-23 11:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0012_invoice_invoice_entity'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoice',
            name='yearmonth',
            field=models.CharField(default=1, max_length=6, verbose_name='対象年月'),
            preserve_default=False,
        ),
    ]