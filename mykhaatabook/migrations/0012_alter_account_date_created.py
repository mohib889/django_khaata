# Generated by Django 3.2.5 on 2021-08-28 20:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mykhaatabook', '0011_alter_account_date_created'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='date_created',
            field=models.DateField(),
        ),
    ]