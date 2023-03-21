# Generated by Django 2.2.16 on 2023-03-21 13:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0008_auto_20230321_1625'),
    ]

    operations = [
        migrations.CreateModel(
            name='RecipeIngredient',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.IntegerField(verbose_name='Количество')),
                ('ingredient', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='api.Ingredient', verbose_name='Ингредиент')),
            ],
            options={
                'verbose_name': 'Ингредиент для рецепта',
                'verbose_name_plural': 'Ингредиенты для рецепта',
                'ordering': ('recipe',),
            },
        ),
        migrations.AlterField(
            model_name='recipe',
            name='ingredients',
            field=models.ManyToManyField(through='api.RecipeIngredient', to='api.Ingredient', verbose_name='Ингредиенты'),
        ),
        migrations.DeleteModel(
            name='IngForRec',
        ),
        migrations.AddField(
            model_name='recipeingredient',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.Recipe', verbose_name='Рецепт'),
        ),
    ]