"""
Metro:
    data = {"meta":{},"request":[{"args":{"store_id":"48215611","eans":["04820192260138"]},"v":"0.1","type":"product.details","id":"product_04820192260138_full"}]}
Auchan:
    data = {"meta":{},"request":[{"args":{"store_id":"48246401","eans":["04820073580485"]},"v":"0.1","type":"product.details","id":"product_04820073580485_full"}]}


data = {"meta": {}, "request": [{"args": {"store_id": "48215611", "eans": ["04820192260138"]}, "v": "0.1", "type": "product.details"}]}
data = {'meta': {}, 'request': [{'args': {'store_id': "48215611", 'eans': ['04820039351791', '04820192260138']}, 'v': '0.1', 'type': 'product.details'}]}

headers = {'Content-type': 'application/json'}
response = requests.post('https://metro.zakaz.ua/api/query.json', json=data, headers=headers)
requests.post('https://metro.zakaz.ua/api/query.json')
"""

import logging
import typing as t
import requests
from copy import deepcopy

from bs4 import BeautifulSoup

from pricecomp.apps.shop.models import Product, RevisionData, Shop

logger = logging.getLogger(__name__)


class ClientError(Exception):
    pass


SHOP_URL_MAP = {
    Shop.metro: 'https://metro.zakaz.ua/api/query.json',
    Shop.auchan: 'https://auchan.zakaz.ua/api/query.json',
}


class ShopClientBase:
    def __init__(self, shop: Shop):
        self._shop = shop

    def request_info(self, products: t.List[Product]) -> t.List[RevisionData]:
        raise NotImplementedError


class ShopClientParse(ShopClientBase):
    def request_info(self, products: t.List[Product]) -> t.List[RevisionData]:
        revisions = []
        for product in products:
            try:
                url = product.get_url(self._shop)
                if not url:
                    continue

                response = self._request(url)
                revision = self._parse(response, product)
            except ClientError as exc:
                logger.exception(exc)
            else:
                revisions.append(revision)
        return revisions

    def _request(self, url) -> requests.Response:
        try:
            r = requests.get(url)
            r.raise_for_status()
        except requests.exceptions.RequestException as exc:
            raise ClientError() from exc
        else:
            return r

    def _parse(self, response: requests.Response, product: Product):
        soup = BeautifulSoup(response.text, 'html.parser')
        price_tag = (soup
                     .find('div', {'class': 'product-details'})
                     .find('div', {'class': 'product-details-info'})
                     .find('span', {'id': 'one-item-price'}))
        image = (soup
                 .find('div', {'class': 'product-details'})
                 .find('div', {'class': 'product-details-main-image'})
                 .find('img'))

        return RevisionData(
            shop_name=self._shop.name,
            product_id=product.id,
            price=price_tag['data'],
            price_3x=None,
            price_6x=None,
            image_url=image.attrs['src'],
        )


class ShopClientAjax(ShopClientBase):
    HEADERS = {'Content-type': 'application/json'}
    REQUEST_DATA_TPL = {
        "meta": {},
        "request": [{
            "args": {
                "store_id": "48215611",
                "eans": ["04820192260138"]
            },
            "v": "0.1",
            "type": "product.details",
        }]
    }

    def request_info(self, products: t.List[Product]) -> t.List[RevisionData]:
        url = SHOP_URL_MAP[self._shop]
        data = self._get_request_data(products)
        if not data:
            return []

        response = requests.post(url, json=data, headers=self.HEADERS)
        return self._parse(response, products)

    def _parse(self, response: requests.Response, products: t.List[Product]) -> t.List[RevisionData]:
        json_data = response.json()
        try:
            items = json_data['responses'][0]['data']['items']
        except (KeyError, IndexError) as exc:
            logger.exception(exc)
            return []

        ean2product = self._get_ean2product(products)
        revisions = []
        for item in items:
            product_id = ean2product[item['ean']]
            image_url = None
            images = item.get('image')
            if images:
                key = sorted(images.keys(), key=lambda s: -len(s))[0]
                image_url = images[key]

            revisions.append(RevisionData(
                shop_name=self._shop.name,
                product_id=product_id,
                price=item['price'],
                price_3x=None,
                price_6x=None,
                image_url=image_url,
            ))

        return revisions

    def _get_request_data(self, products: t.List[Product]):
        eans = [p.get_ean(self._shop) for p in products]
        eans = [ean for ean in eans if ean]
        if not eans:
            return None

        data = deepcopy(self.REQUEST_DATA_TPL)
        data['request'][0]['args']['store_id'] = str(self._shop.value)
        data['request'][0]['args']['eans'] = eans
        return data

    def _get_ean2product(self, products: t.List[Product]):
        return {p.get_ean(self._shop): p.id for p in products
                if p.get_ean(self._shop)}


def client_factory(shop: Shop):
    return {
        shop.metro: ShopClientAjax,
        shop.auchan: ShopClientAjax,
        shop.fozi: ShopClientParse,
        shop.novus: ShopClientParse,
    }[shop](shop)
