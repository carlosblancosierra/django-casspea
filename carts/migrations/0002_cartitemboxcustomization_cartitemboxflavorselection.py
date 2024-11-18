# Generated by Django 5.1.3 on 2024-11-17 22:42

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('allergens', '0001_initial'),
        ('carts', '0001_initial'),
        ('flavours', '0004_alter_flavour_image'),
    ]

    operations = [
        migrations.CreateModel(
            name='CartItemBoxCustomization',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('selection_type', models.CharField(choices=[('RANDOM', 'Random'), ('PICK_AND_MIX', 'Pick and Mix')], max_length=20)),
                ('allergens', models.ManyToManyField(blank=True, to='allergens.allergen')),
                ('cart_item', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='box_customization', to='carts.cartitem')),
            ],
        ),
        migrations.CreateModel(
            name='CartItemBoxFlavorSelection',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField(default=1)),
                ('box_customization', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='flavor_selections', to='carts.cartitemboxcustomization')),
                ('flavor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='flavours.flavour')),
            ],
        ),
    ]