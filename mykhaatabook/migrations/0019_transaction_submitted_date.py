# Generated by Django 3.2.7 on 2022-02-01 19:21

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('mykhaatabook', '0018_auto_20220128_0150'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='submitted_date',
            field=models.DateTimeField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
