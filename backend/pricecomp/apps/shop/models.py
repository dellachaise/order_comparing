from django.db import models


class Product(models.Model):
    name = models.CharField(max_length=200)
    order = models.IntegerField(default=0)
    metro = models.URLField()
    fozi = models.URLField()
    auchan = models.URLField()
    novus = models.URLField()

    @property
    def metro_id(self):
        return _parse_url(self.metro)

    @property
    def fozi_id(self):
        return _parse_url(self.fozi)

    @property
    def auchan_id(self):
        return _parse_url(self.auchan)

    @property
    def novus_id(self):
        return _parse_url(self.novus)


def _parse_url(url):
    # https://metro.zakaz.ua/ru/05201360532506/%D0%
    parts = url.split('/')
    for p in parts:
        if len(p) < 10:
            continue
        try:
            if str(int(p)) == p:
                return int(p)
        except ValueError:
            continue
