import logging
import typing as t
from enum import Enum

from dataclasses import dataclass
from django.db import models

logger = logging.getLogger(__name__)


class Shop(Enum):
    metro: int = 48215611
    fozi: int = 2
    auchan: int = 48246401
    novus: int = 3


SHOP_SHOOISES = [(s.name, s.name) for s in Shop]


@dataclass
class OutdatedRevisions:
    shop: Shop
    products_ids: t.Collection[int]


@dataclass
class RevisionData:
    shop_name: str
    product_id: int
    price: int
    price_3x: t.Optional[int]
    price_6x: t.Optional[int]
    image_url: str


class Product(models.Model):
    name = models.CharField(max_length=200)
    metro = models.URLField(blank=True, null=True)
    fozi = models.URLField(blank=True, null=True)
    auchan = models.URLField(blank=True, null=True)
    novus = models.URLField(blank=True, null=True)

    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_url(self, shop: Shop):
        return {
            Shop.metro: self.metro,
            Shop.fozi: self.fozi,
            Shop.auchan: self.auchan,
            Shop.novus: self.novus,
        }[shop]

    def get_ean(self, shop: Shop):
        url = {
            Shop.metro: self.metro,
            Shop.fozi: self.fozi,
            Shop.auchan: self.auchan,
            Shop.novus: self.novus,
        }[shop]
        if not url:
            return None
        return _parse_url(url)

    def __str__(self):
        return f"{self.name} (active: {self.is_active})"


class ProductRevision(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE,
                                related_name='revisions')
    shop = models.CharField(max_length=20, choices=SHOP_SHOOISES)
    price = models.IntegerField()
    price_3x = models.IntegerField(blank=True, null=True)
    price_6x = models.IntegerField(blank=True, null=True)
    image_url = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.product_id} {self.shop} {self.price}"


def _parse_url(url: str) -> str:
    # https://metro.zakaz.ua/ru/05201360532506/%D0%
    parts = url.split('/')
    for p in parts:
        if len(p) < 10:
            continue
        try:
            if p.isdigit():
                return p
        except ValueError as exc:
            continue
