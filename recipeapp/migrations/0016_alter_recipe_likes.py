# Generated by Django 4.2.9 on 2024-01-27 11:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipeapp', '0015_profile_following_alter_profile_followers'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='likes',
            field=models.ManyToManyField(related_name='liked_recipes', to='recipeapp.profile'),
        ),
    ]
