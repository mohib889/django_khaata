# Generated by Django 3.2.5 on 2021-08-13 19:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mykhaatabook', '0006_auto_20210811_0036'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='transaction_type',
            field=models.CharField(blank=True, choices=[('Credit', 'Credit'), ('Debit', 'Debit'), ('None', 'None')], default='Credit', help_text='رقم کی قسم: CR یا DR', max_length=32, null=True),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='refernce_number',
            field=models.CharField(default='000000', max_length=366),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='transaction_type',
            field=models.CharField(choices=[('Credit', 'Credit'), ('Debit', 'Debit'), ('None', 'None')], help_text='رقم کی قسم: کریڈٹ یا ڈیبٹ', max_length=32),
        ),
    ]
