# Generated by Django 5.1.1 on 2024-10-10 00:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('evapp', '0015_evcar'),
    ]

    operations = [
        migrations.CreateModel(
            name='UsedCar',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('차종', models.CharField(max_length=255)),
                ('모델명', models.CharField(max_length=255)),
                ('출고일', models.CharField(max_length=7)),
                ('주행거리', models.IntegerField()),
                ('가격', models.DecimalField(decimal_places=0, max_digits=10)),
                ('신차가격', models.DecimalField(decimal_places=0, max_digits=10)),
            ],
            options={
                'db_table': 'used_car',
                'managed': False,
            },
        ),
    ]