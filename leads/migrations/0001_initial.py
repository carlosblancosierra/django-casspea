# Generated by Django 5.1.3 on 2024-12-01 12:03

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Lead",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("email", models.EmailField(max_length=254)),
                (
                    "lead_type",
                    models.CharField(
                        choices=[
                            ("newsletter", "Newsletter Subscriber"),
                            ("contact_form", "Contact Form"),
                        ],
                        max_length=100,
                    ),
                ),
                ("unsubscribed", models.BooleanField(default=False)),
                ("created", models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]