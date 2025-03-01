# Generated by Django 5.1.6 on 2025-02-28 12:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('railway', '0005_train_operating_days_data'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='train',
            name='running_days',
        ),
        migrations.RemoveField(
            model_name='train',
            name='operating_days_data',
        ),
        migrations.AddField(
            model_name='train',
            name='friday',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='train',
            name='monday',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='train',
            name='saturday',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='train',
            name='sunday',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='train',
            name='thursday',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='train',
            name='tuesday',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='train',
            name='wednesday',
            field=models.BooleanField(default=False),
        ),
        migrations.DeleteModel(
            name='Day',
        ),
    ]
