# Generated by Django 5.1.1 on 2024-09-30 05:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('evapp', '0005_car_보조금_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='users',
            name='address',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
