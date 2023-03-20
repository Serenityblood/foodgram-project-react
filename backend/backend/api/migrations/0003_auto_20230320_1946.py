# Generated by Django 2.2.16 on 2023-03-20 16:46

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_auto_20230320_1824'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shoppingcard',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='shopping_card', to=settings.AUTH_USER_MODEL),
        ),
    ]
