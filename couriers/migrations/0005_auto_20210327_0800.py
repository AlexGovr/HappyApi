# Generated by Django 3.1.7 on 2021-03-27 08:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('couriers', '0004_order'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='assign_time',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='complete_time',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='completed',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='order',
            name='courier_id',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='couriers.courier'),
        ),
    ]
