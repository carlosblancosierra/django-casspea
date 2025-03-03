from django.db import models

# Create your models here.
class Allergen(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)


    def __str__(self):
        return self.name
