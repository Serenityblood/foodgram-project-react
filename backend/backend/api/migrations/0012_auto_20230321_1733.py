# Generated by Django 2.2.16 on 2023-03-21 14:33

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('api', '0011_auto_20230321_1658'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='ShoppingCard',
            new_name='ShoppingCart',
        ),
    ]