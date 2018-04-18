from rest_framework import serializers, viewsets

from pricecomp.apps.shop.models import Product


class ProductSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Product
        fields = ('name', 'metro', 'fozzy', 'auchan', 'novus')


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
