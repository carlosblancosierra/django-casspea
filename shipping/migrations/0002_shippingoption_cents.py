# Generated by Django 5.1.4 on 2024-12-06 14:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("shipping", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="shippingoption",
            name="cents",
            field=models.PositiveIntegerField(blank=True, default=499, null=True),
        ),
    ]
