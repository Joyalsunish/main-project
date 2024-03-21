# Generated by Django 4.2.6 on 2023-11-16 08:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipeapp', '0009_recipe_likes'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='recipe',
            name='likes',
        ),
        migrations.AddField(
            model_name='recipe',
            name='likes',
            field=models.ManyToManyField(default=0, related_name='liked_recipes', to='recipeapp.profile'),
        ),
    ]
