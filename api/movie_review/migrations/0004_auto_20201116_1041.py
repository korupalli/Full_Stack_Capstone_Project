# Generated by Django 3.0.5 on 2020-11-15 23:41

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('movie_review', '0003_auto_20201114_1109'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reviews',
            name='review_date',
            field=models.DateField(default=datetime.date(2020, 11, 16)),
        ),
        migrations.AlterField(
            model_name='reviews',
            name='review_time',
            field=models.TimeField(default=datetime.time(10, 41, 27, 778214)),
        ),
    ]
