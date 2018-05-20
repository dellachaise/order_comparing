import datetime as dt
import logging
import typing as t
from collections import defaultdict

from dataclasses import dataclass
from django.shortcuts import render
from rest_framework import serializers, viewsets

from pricecomp.apps.shop import models as m
from pricecomp.apps.shop.client import client_factory

logger = logging.getLogger(__name__)

REVISION_EXPIRE_HOURS = 120


@dataclass
class ProductPrices:
    id: int
    name: str
    price_metro: int
    price_fozi: int
    price_auchan: int
    price_novus: int
    image: str = None


def products_list(request):
    products = _get_products()
    shop_product_id2price = fetch_shop_product_id2price([p.id for p in products])
    print("shop_product_id2price", shop_product_id2price)
    product_id2image = {}

    products_prices = [ProductPrices(
        id=product.id,
        name=product.name,
        image=product_id2image.get(product.id),
        price_metro=shop_product_id2price.get((m.Shop.metro.name, product.id), ''),
        price_fozi=shop_product_id2price.get((m.Shop.fozi.name, product.id), ''),
        price_auchan=shop_product_id2price.get((m.Shop.auchan.name, product.id), ''),
        price_novus=shop_product_id2price.get((m.Shop.novus.name, product.id), ''),
    ) for product in products]
    return render(request, 'shop/products_list.html', {'products': products_prices})


class ProductSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = m.Product
        fields = ('name', 'metro', 'fozi', 'auchan', 'novus')

    def to_representation(self, instance):
        data = super().to_representation(instance)
        print(data)
        return data


class ProductViewSet(viewsets.ModelViewSet):
    queryset = m.Product.objects.all()
    serializer_class = ProductSerializer

    def get_queryset(self):
        queryset = m.Product.objects.filter(is_active=True)
        expired_products = get_expired_products(queryset)
        if not expired_products:
            return queryset

        update_revisions_info(expired_products)
        return queryset


def get_expired_products(products=t.List[m.Product]
                         ) -> t.Collection[m.OutdatedRevisions]:
    shop2required_products_ids = defaultdict(list)
    for product in products:
        for shop in m.Shop:
            if product.get_url(shop):
                shop2required_products_ids[shop].append(product.id)

    min_created_at = dt.datetime.utcnow() - dt.timedelta(hours=REVISION_EXPIRE_HOURS)
    revision_query = (m.ProductRevision.objects
                      .values_list('product_id', flat=True)
                      .filter(created_at__gte=min_created_at))

    expired_products = []
    for shop, products_ids in shop2required_products_ids.items():
        existed_ids = revision_query.filter(shop=shop.name,
                                            product_id__in=products_ids)
        outdated_products_ids = set(products_ids) - set(existed_ids)
        if outdated_products_ids:
            expired_products.append(m.OutdatedRevisions(
                shop=shop,
                products_ids=outdated_products_ids,
            ))
    return expired_products


def update_revisions_info(outdated_revisions: t.Collection[m.OutdatedRevisions]):
    products_ids = set().union(*(r.products_ids for r in outdated_revisions))
    product_id2product = fetch_product_id2product(products_ids)

    shop2products = {o_revision.shop: [product_id2product[pid]
                                            for pid in o_revision.products_ids]
                     for o_revision in outdated_revisions}

    for shop, products in shop2products.items():
        client = client_factory(shop)
        revisions_data = client.request_info(products)
        for revision_data in revisions_data:
            product_revision = m.ProductRevision(
                product_id=revision_data.product_id,
                shop=revision_data.shop_name,
                price=revision_data.price,
                price_3x=revision_data.price_3x,
                price_6x=revision_data.price_6x,
                image_url=revision_data.image_url,
            )
            product_revision.save()


def fetch_product_id2product(products_ids):
    query = m.Product.objects.filter(id__in=products_ids)
    return {p.id: p for p in query}


def fetch_shop_product_id2price(products_ids: t.List[int]):
    min_created_at = dt.datetime.utcnow() - dt.timedelta(hours=REVISION_EXPIRE_HOURS)
    query = m.ProductRevision.objects.filter(product_id__in=products_ids,
                                             created_at__gte=min_created_at)
    return {(p.shop, p.product_id): p.price/100 for p in query}

def _get_products():
    queryset = m.Product.objects.filter(is_active=True)
    expired_products = get_expired_products(queryset)
    if not expired_products:
        return queryset

    update_revisions_info(expired_products)
    return queryset
