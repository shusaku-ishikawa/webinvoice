# Generated by Django 2.1.5 on 2019-04-23 12:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0013_invoice_yearmonth'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoice',
            name='pdf',
            field=models.FileField(null=True, upload_to='invoice_pdf', verbose_name='出力PDF'),
        ),
    ]