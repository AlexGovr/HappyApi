# Generated by Django 3.1.7 on 2021-03-25 06:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('couriers', '0002_auto_20210322_1805'),
    ]

    operations = [
        migrations.AlterField(
            model_name='courier',
            name='regions',
            field=models.CharField(max_length=120),
        ),
        migrations.AlterField(
            model_name='courier',
            name='working_hours',
            field=models.CharField(max_length=240),
        ),
    ]
