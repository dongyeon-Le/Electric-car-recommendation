# Generated by Django 5.1.1 on 2024-10-02 07:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('evapp', '0010_remove_users_del_flag_remove_users_verified'),
    ]

    operations = [
        migrations.AddField(
            model_name='users',
            name='delete_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]