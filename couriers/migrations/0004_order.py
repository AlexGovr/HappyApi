# Generated by Django 3.1.7 on 2021-03-26 04:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('couriers', '0003_auto_20210325_0653'),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('order_id', models.IntegerField(primary_key=True, serialize=False)),
                ('region', models.IntegerField()),
                ('weight', models.FloatField()),
                ('delivery_hours', models.CharField(max_length=240)),
            ],
        ),
    ]
