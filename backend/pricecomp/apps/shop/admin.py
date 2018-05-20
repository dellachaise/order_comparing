from django.contrib import admin

from pricecomp.apps.shop.models import Product, ProductRevision


admin.site.register(Product)


@admin.register(ProductRevision)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'shop', 'price', 'created_at')

    def product_name(self, obj):
        return obj.product.name
