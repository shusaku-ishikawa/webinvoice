# Generated by Django 2.1.5 on 2019-04-25 12:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0017_bankinfo'),
    ]

    operations = [
        migrations.AddField(
            model_name='bankinfo',
            name='meigi',
            field=models.CharField(default=1, max_length=50, verbose_name='名義'),
            preserve_default=False,
        ),
    ]