# Generated by Django 2.2.16 on 2023-03-21 13:24

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0006_auto_20230321_1612'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='favorite',
            options={'ordering': ('recipe',), 'verbose_name': 'Избранный', 'verbose_name_plural': 'Избранные'},
        ),
        migrations.AlterModelOptions(
            name='ingforrec',
            options={'ordering': ('recipe',), 'verbose_name': 'Ингредиент для рецепта', 'verbose_name_plural': 'Ингредиенты для рецепта'},
        ),
        migrations.AlterModelOptions(
            name='ingredient',
            options={'ordering': ('name',), 'verbose_name': 'Ингредиент', 'verbose_name_plural': 'Ингредиенты'},
        ),
        migrations.AlterModelOptions(
            name='recipe',
            options={'ordering': ('pub_date',), 'verbose_name': 'Рецепт', 'verbose_name_plural': 'Рецепты'},
        ),
        migrations.AlterModelOptions(
            name='shoppingcard',
            options={'ordering': ('recipe',), 'verbose_name': 'Лист покупок', 'verbose_name_plural': 'Листы покупок'},
        ),
        migrations.AlterField(
            model_name='recipe',
            name='cooking_time',
            field=models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1, message='Не может быть меньше 1')], verbose_name='Время готовки'),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='name',
            field=models.CharField(max_length=200, verbose_name='Название'),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='tags',
            field=models.ManyToManyField(to='api.Tag', verbose_name='Тэги'),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='text',
            field=models.TextField(verbose_name='Описание'),
        ),
    ]