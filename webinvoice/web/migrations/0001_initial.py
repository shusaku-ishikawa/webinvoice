# Generated by Django 2.1.5 on 2019-05-21 05:39

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import web.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='BankInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bank', models.CharField(default='xxx銀行', max_length=20, verbose_name='金融機関名')),
                ('branch', models.CharField(default='xxx支店', max_length=20, verbose_name='支店名')),
                ('type', models.CharField(choices=[('普通', '普通'), ('当座', '当座')], default='普通', max_length=20, verbose_name='口座種別')),
                ('number', models.CharField(default='00000', max_length=20, verbose_name='口座番号')),
                ('meigi', models.CharField(max_length=50, verbose_name='名義')),
            ],
            options={
                'verbose_name': '口座情報',
                'verbose_name_plural': '口座情報',
            },
        ),
        migrations.CreateModel(
            name='Company',
            fields=[
                ('id', models.CharField(max_length=50, primary_key=True, serialize=False, unique=True, verbose_name='会社ID')),
                ('corporate_number', models.CharField(max_length=50, unique=True, validators=[django.core.validators.RegexValidator('^[0-9a-zA-Z_]*$', 'IDは英数字もしくはアンダースコア(_)のみとしてください')], verbose_name='法人番号')),
                ('kana_name', models.CharField(max_length=50, verbose_name='契約者名カナ')),
                ('kanji_name', models.CharField(max_length=50, verbose_name='契約者名漢字')),
                ('zip', models.CharField(max_length=10, validators=[web.models.validate_postcode], verbose_name='契約者郵便番号')),
                ('address_pref', models.CharField(choices=[('東京都', '東京都'), ('北海道', '北海道'), ('秋田県', '秋田県')], max_length=10, verbose_name='契約者都道府県')),
                ('address_city', models.CharField(max_length=30, verbose_name='契約者市区町村')),
                ('address_street', models.CharField(max_length=50, verbose_name='契約者住所番地以降')),
                ('address_bld', models.CharField(blank=True, max_length=50, null=True, verbose_name='契約者住所建物名')),
                ('telephone_1', models.CharField(blank=True, max_length=20, null=True, validators=[web.models.validate_phonenumber], verbose_name='連絡先電話番号1')),
                ('telephone_2', models.CharField(blank=True, max_length=20, null=True, validators=[web.models.validate_phonenumber], verbose_name='連絡先電話番号2')),
                ('fax', models.CharField(blank=True, max_length=20, null=True, validators=[web.models.validate_phonenumber], verbose_name='FAX番号')),
                ('hp_url', models.CharField(blank=True, max_length=20, null=True, verbose_name='URL')),
                ('owner_name', models.CharField(blank=True, max_length=50, null=True, verbose_name='代表者名')),
                ('representative_name', models.CharField(blank=True, max_length=50, null=True, verbose_name='担当者名')),
                ('email', models.EmailField(blank=True, max_length=254, null=True, verbose_name='メール')),
                ('note', models.TextField(blank=True, null=True)),
                ('registered_at', models.DateTimeField(auto_now_add=True, verbose_name='登録日')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新日')),
                ('deleted', models.BooleanField(default=False, verbose_name='削除フラグ')),
                ('registered_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='company_registered', to=settings.AUTH_USER_MODEL, verbose_name='登録者')),
                ('updated_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='company_updated', to=settings.AUTH_USER_MODEL, verbose_name='更新者')),
            ],
            options={
                'verbose_name': '会社',
                'verbose_name_plural': '会社',
                'ordering': ['pk'],
            },
        ),
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('invoice_code', models.CharField(max_length=50, primary_key=True, serialize=False, verbose_name='請求書ID')),
                ('pdf', models.FileField(null=True, upload_to='invoice_pdf', verbose_name='出力PDF')),
                ('invoice_printed_at', models.DateField(auto_now_add=True, verbose_name='発行日')),
                ('registered_at', models.DateTimeField(auto_now_add=True, verbose_name='登録日')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新日')),
                ('deleted', models.BooleanField(default=False, verbose_name='削除フラグ')),
                ('registered_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='invoice_registered', to=settings.AUTH_USER_MODEL, verbose_name='登録者')),
                ('updated_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='invoice_updated', to=settings.AUTH_USER_MODEL, verbose_name='更新者')),
            ],
            options={
                'verbose_name': '請求書',
                'verbose_name_plural': '請求書',
                'ordering': ['pk'],
            },
        ),
        migrations.CreateModel(
            name='InvoiceDetail',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product_category_1', models.CharField(max_length=50, verbose_name='商材大区分')),
                ('product_category_2', models.CharField(max_length=50, verbose_name='商材小区分')),
                ('yearmonth', models.CharField(max_length=6, verbose_name='請求月')),
                ('seq_number', models.CharField(max_length=50, verbose_name='SEQNO')),
                ('order_number', models.CharField(max_length=50, verbose_name='申込管理番号')),
                ('invoice_code', models.CharField(max_length=50, verbose_name='請求書ID')),
                ('service_start_date', models.DateField(verbose_name='サービス開始日')),
                ('service_name', models.CharField(max_length=50, verbose_name='請求明細内容')),
                ('invoice_amount_wo_tax', models.IntegerField(verbose_name='請求金額(税抜)')),
                ('tax_type', models.CharField(choices=[('課税', '課税'), ('非課税', '非課税')], max_length=10, verbose_name='税区分')),
                ('tax_rate_perc', models.IntegerField(verbose_name='税率')),
                ('tax_amount', models.IntegerField(verbose_name='請求金額(税額)')),
                ('note', models.TextField(blank=True, null=True, verbose_name='備考')),
                ('registered_at', models.DateTimeField(auto_now_add=True, verbose_name='登録日')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新日')),
                ('deleted', models.BooleanField(default=False, verbose_name='削除フラグ')),
                ('invoice', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='details', to='web.Invoice', verbose_name='請求書')),
            ],
            options={
                'verbose_name': '請求明細',
                'verbose_name_plural': '請求明細',
                'ordering': ['pk'],
            },
        ),
        migrations.CreateModel(
            name='InvoiceEntity',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('invoice_zip', models.CharField(max_length=10, validators=[web.models.validate_postcode], verbose_name='請求郵便番号')),
                ('invoice_address_pref', models.CharField(choices=[('東京都', '東京都'), ('北海道', '北海道'), ('秋田県', '秋田県')], max_length=10, verbose_name='請求都道府県')),
                ('invoice_address_city', models.CharField(max_length=30, verbose_name='請求市区町村')),
                ('invoice_address_street', models.CharField(max_length=50, verbose_name='請求住所番地以降')),
                ('invoice_address_bld', models.CharField(blank=True, max_length=50, null=True, verbose_name='請求住所建物名')),
                ('invoice_company_name', models.CharField(blank=True, max_length=100, null=True, verbose_name='請求会社名')),
                ('invoice_dept', models.CharField(blank=True, max_length=100, null=True, verbose_name='請求部署')),
                ('invoice_person', models.CharField(blank=True, max_length=50, null=True, verbose_name='請求宛名')),
                ('invoice_project_1', models.CharField(blank=True, max_length=50, null=True, verbose_name='請求宛名1')),
                ('invoice_project_2', models.CharField(blank=True, max_length=50, null=True, verbose_name='請求宛名2')),
                ('invoice_project_3', models.CharField(blank=True, max_length=50, null=True, verbose_name='請求宛名3')),
                ('payment_method', models.CharField(choices=[('クレカ', 'クレカ'), ('引落', '引落'), ('振込', '振込')], default='振込', max_length=20, verbose_name='支払い方法')),
                ('invoice_closed_at', models.CharField(blank=True, choices=[('末日', '末日'), ('20日', '20日')], max_length=20, null=True, verbose_name='締め日')),
                ('payment_due_to', models.CharField(blank=True, choices=[('末日', '末日'), ('20日', '20日')], max_length=20, null=True, verbose_name='支払い期日')),
                ('invoice_sent_at', models.CharField(blank=True, choices=[('末日', '末日'), ('20日', '20日')], max_length=20, null=True, verbose_name='請求書送付時期')),
                ('invoice_timing', models.CharField(blank=True, choices=[('売掛', '売掛'), ('前入金', '前入金')], max_length=20, null=True, verbose_name='請求タイミング')),
                ('invoice_period', models.CharField(blank=True, choices=[('毎月', '毎月'), ('6ヶ月', '6ヶ月')], max_length=20, null=True, verbose_name='請求周期')),
                ('bank_name', models.CharField(blank=True, max_length=20, null=True, verbose_name='振込銀行名')),
                ('bank_branch_name', models.CharField(blank=True, max_length=20, null=True, verbose_name='振込支店名')),
                ('bank_account_type', models.CharField(blank=True, choices=[('普通', '普通'), ('当座', '当座')], max_length=20, null=True, verbose_name='口座種類')),
                ('bank_account_number', models.CharField(blank=True, max_length=20, null=True, verbose_name='口座番号')),
                ('credit_card_settlement_company', models.CharField(blank=True, max_length=20, null=True, verbose_name='クレカ決済会社')),
                ('credit_card_code', models.CharField(blank=True, max_length=20, null=True, verbose_name='クレカコード')),
                ('credit_card_id', models.CharField(blank=True, max_length=20, null=True, verbose_name='クレカID')),
                ('settlement_company', models.CharField(blank=True, max_length=20, null=True, verbose_name='決済会社')),
                ('settlement_code', models.CharField(blank=True, max_length=20, null=True, verbose_name='決済コード')),
                ('settlement_id', models.CharField(blank=True, max_length=20, null=True, verbose_name='決済ID')),
                ('note', models.TextField(blank=True, null=True, verbose_name='特記事項')),
                ('registered_at', models.DateTimeField(auto_now_add=True, verbose_name='登録日')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新日')),
                ('deleted', models.BooleanField(default=False, verbose_name='削除フラグ')),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='web.Company', verbose_name='会社')),
                ('registered_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='entity_registered', to=settings.AUTH_USER_MODEL, verbose_name='登録者')),
                ('updated_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='entity_updated', to=settings.AUTH_USER_MODEL, verbose_name='更新者')),
            ],
            options={
                'verbose_name': '請求管理簿',
                'verbose_name_plural': '請求管理簿',
                'ordering': ['pk'],
            },
        ),
        migrations.CreateModel(
            name='OurInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('zip', models.CharField(max_length=100, verbose_name='郵便番号')),
                ('address_1', models.CharField(max_length=100, verbose_name='住所1')),
                ('address_2', models.CharField(max_length=100, verbose_name='住所2')),
                ('phone', models.CharField(max_length=100, verbose_name='電話番号')),
            ],
        ),
        migrations.CreateModel(
            name='UploadedFile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[(1, '会社情報'), (2, '請求管理簿'), (3, '請求明細')], max_length=10, verbose_name='ファイル種類')),
                ('file', models.FileField(upload_to='company_csv', validators=[django.core.validators.FileExtensionValidator(['xlsx'])], verbose_name='アップロードファイル')),
                ('processed_at', models.DateTimeField(auto_now_add=True, verbose_name='処理日')),
                ('record_count', models.IntegerField(default=0, verbose_name='件数')),
                ('uploaded_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='実行ユーザ')),
            ],
            options={
                'verbose_name': 'アップロード',
                'verbose_name_plural': 'アップロードファイル',
                'ordering': ['pk'],
            },
        ),
        migrations.CreateModel(
            name='UploadedFileError',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('row_index', models.IntegerField(verbose_name='行番号')),
                ('error', models.CharField(blank=True, max_length=255, null=True, verbose_name='エラー')),
                ('file', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='errors', to='web.UploadedFile')),
            ],
        ),
        migrations.AddField(
            model_name='invoicedetail',
            name='invoice_entity',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='my_invoice_details', to='web.InvoiceEntity', verbose_name='請求管理簿'),
        ),
        migrations.AddField(
            model_name='invoicedetail',
            name='registered_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='detail_registered', to=settings.AUTH_USER_MODEL, verbose_name='登録者'),
        ),
        migrations.AddField(
            model_name='invoicedetail',
            name='updated_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='detail_updated', to=settings.AUTH_USER_MODEL, verbose_name='更新者'),
        ),
    ]
