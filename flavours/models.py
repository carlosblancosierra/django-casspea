from django.db import models
from allergens.models import Allergen

# Create your models here.
class FlavourCategoryManager(models.Manager):
    def active(self):
        return self.filter(active=True)

class FlavourCategory(models.Model):
    name = models.CharField(max_length=255)
    active = models.BooleanField(default=True)
    slug = models.SlugField(unique=True)

    objects = FlavourCategoryManager()

    def __str__(self):
        return self.name

class FlavourManager(models.Manager):
    def active(self):
        return self.filter(active=True)

class Flavour(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    mini_description = models.TextField()
    allergens = models.ManyToManyField(Allergen)
    image = models.URLField(max_length=500)
    category = models.ForeignKey(FlavourCategory, on_delete=models.CASCADE, default=1)

    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    objects = FlavourManager()

    def __str__(self):
        return self.name
