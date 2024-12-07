# Generated by Django 5.1.4 on 2024-12-07 18:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("addresses", "0004_alter_address_unique_together"),
    ]

    operations = [
        migrations.AddField(
            model_name="address",
            name="first_name",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="address",
            name="last_name",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name="address",
            name="full_name",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
