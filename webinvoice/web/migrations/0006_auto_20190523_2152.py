# Generated by Django 2.1.5 on 2019-05-23 12:52

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0005_auto_20190523_2040'),
    ]

    operations = [
        migrations.AlterField(
            model_name='handwritteninvoice',
            name='date_created',
            field=models.DateField(default=datetime.datetime(2019, 5, 23, 12, 52, 34, 581924, tzinfo=utc), verbose_name='作成日'),
        ),
    ]
