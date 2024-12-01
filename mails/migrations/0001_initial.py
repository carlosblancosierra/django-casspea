# Generated by Django 5.1.3 on 2024-12-01 12:03

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("contenttypes", "0002_remove_content_type_name"),
    ]

    operations = [
        migrations.CreateModel(
            name="EmailType",
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
                (
                    "name",
                    models.CharField(
                        choices=[
                            ("newsletter", "Newsletter"),
                            ("contact", "Contact"),
                            ("order_paid", "Order Paid"),
                        ],
                        max_length=50,
                        unique=True,
                    ),
                ),
                ("template_name", models.CharField(max_length=50, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name="EmailSent",
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
                ("object_id", models.PositiveIntegerField()),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "Pending"),
                            ("sent", "Sent"),
                            ("failed", "Failed"),
                        ],
                        default="pending",
                        max_length=10,
                    ),
                ),
                ("error_message", models.TextField(blank=True, null=True)),
                ("sent", models.DateTimeField(blank=True, null=True)),
                ("created", models.DateTimeField(auto_now_add=True)),
                (
                    "content_type",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="contenttypes.contenttype",
                    ),
                ),
                (
                    "email_type",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="mails.emailtype",
                    ),
                ),
            ],
        ),
    ]