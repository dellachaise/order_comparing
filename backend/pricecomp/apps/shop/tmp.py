from pricecomp.apps.shop.client import *
from pricecomp.apps.shop.models import *
from pricecomp.apps.shop.views import update_revisions_info, get_expired_products
products = Product.objects.all()
outdated_revisions = get_expired_products(products)
update_revisions_info(outdated_revisions)
