# Generated by Django 5.1.6 on 2025-02-28 14:02

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('railway', '0008_day'),
    ]

    operations = [
        migrations.AlterField(
            model_name='intermediatestation',
            name='train',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='stations', to='railway.train'),
        ),
    ]
