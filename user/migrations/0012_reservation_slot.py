# Generated by Django 5.1.1 on 2025-02-01 21:18

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0011_reservationlog'),
    ]

    operations = [
        migrations.AddField(
            model_name='reservation',
            name='slot',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, related_name='reservations', to='user.slot'),
            preserve_default=False,
        ),
    ]
