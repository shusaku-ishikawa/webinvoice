# Generated by Django 2.1.5 on 2019-03-14 04:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0002_auto_20190314_1310'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoice',
            name='code',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='請求番号'),
        ),
    ]
