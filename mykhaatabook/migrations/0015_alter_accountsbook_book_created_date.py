# Generated by Django 3.2.5 on 2021-08-28 20:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mykhaatabook', '0014_alter_transaction_slip'),
    ]

    operations = [
        migrations.AlterField(
            model_name='accountsbook',
            name='book_created_date',
            field=models.DateTimeField(),
        ),
    ]
