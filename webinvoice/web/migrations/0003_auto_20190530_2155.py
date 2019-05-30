# Generated by Django 2.1.5 on 2019-05-30 12:55

import datetime
from django.db import migrations, models
import django.db.models.deletion
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0002_auto_20190530_1353'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='invoice',
            name='deleted',
        ),
        migrations.AlterField(
            model_name='handwritteninvoice',
            name='date_created',
            field=models.DateField(default=datetime.datetime(2019, 5, 30, 12, 55, 52, 762501, tzinfo=utc), verbose_name='作成日'),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='id',
            field=models.CharField(max_length=50, primary_key=True, serialize=False, unique=True, verbose_name='請求書ID'),
        ),
        migrations.AlterField(
            model_name='invoicedetail',
            name='id',
            field=models.CharField(max_length=50, primary_key=True, serialize=False, unique=True, verbose_name='請求明細ID'),
        ),
        migrations.AlterField(
            model_name='invoicedetail',
            name='invoice',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='details', to='web.Invoice', verbose_name='請求書'),
        ),
    ]