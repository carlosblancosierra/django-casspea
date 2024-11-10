from django.db import models

class ProductCategoryManager(models.Manager):
    def active(self):
        return self.filter(active=True)

class ProductCategory(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    description = models.TextField()

    active = models.BooleanField(default=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    objects = ProductCategoryManager()

    def __str__(self):
        return self.name


class ProductManager(models.Manager):
    def active(self):
        return self.filter(active=True)

class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE)

    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    stripe_price_id = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    weight = models.IntegerField(help_text="Weight in grams")

    active = models.BooleanField(default=True)
    sold_out = models.BooleanField(default=False)

    units_per_box = models.IntegerField(help_text="Number of chocolates in the box")

    main_color = models.CharField(max_length=255)
    secondary_color = models.CharField(max_length=255)

    seo_title = models.CharField(max_length=255)
    seo_description = models.CharField(max_length=255)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    objects = ProductManager()

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['base_price']
