from django.db.models import Q

from store.models import Product


class ProductCatalogService:
    def list_products(self, category_slug=None, query=None):
        products = Product.objects.filter(is_active=True).select_related("category")
        if category_slug:
            products = products.filter(category__slug=category_slug)
        if query:
            products = products.filter(Q(name__icontains=query) | Q(anime_title__icontains=query))
        return products.order_by("-popularity_score", "name")


class ProductCatalogProxy:
    """Заместитель для клиентского каталога: фильтрует активные товары и кэширует выдачу."""

    _cache = {}

    def __init__(self, service=None):
        self.service = service or ProductCatalogService()

    def list_products(self, category_slug=None, query=None):
        key = (category_slug or "", query or "")
        if key not in self._cache:
            self._cache[key] = list(self.service.list_products(category_slug, query))
        return self._cache[key]

    @classmethod
    def clear_cache(cls):
        cls._cache.clear()
