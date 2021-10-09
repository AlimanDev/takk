from django.contrib import admin
from apps.products import models

admin.site.register(models.Modifier)
admin.site.register(models.ModifierItem)
admin.site.register(models.ProductCategory)
admin.site.register(models.Product)
admin.site.register(models.ProductSize)
admin.site.register(models.CafeProductState)

