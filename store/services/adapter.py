class LegacyAnimeTrendClient:
    """Новый внешний модуль с неудобным форматом данных."""

    def load_hot_titles(self):
        return [
            {"name": "Jujutsu Kaisen", "heatIndex": 96},
            {"name": "Chainsaw Man", "heatIndex": 91},
            {"name": "Demon Slayer", "heatIndex": 88},
            {"name": "One Piece", "heatIndex": 86},
        ]


class AnimeTrendAdapter:
    """Адаптер приводит тренды к интерфейсу рекомендаций магазина."""

    def __init__(self, client=None):
        self.client = client or LegacyAnimeTrendClient()

    def recommended_products(self, limit=4):
        from store.models import Product

        hot_titles = self.client.load_hot_titles()
        heat_by_title = {item["name"]: item["heatIndex"] for item in hot_titles}
        products = list(
            Product.objects.filter(is_active=True, anime_title__in=heat_by_title)
            .select_related("category")
            .order_by("-popularity_score")
        )
        products.sort(key=lambda product: heat_by_title.get(product.anime_title, 0), reverse=True)
        return products[:limit]

    def labels(self):
        return [item["name"] for item in self.client.load_hot_titles()]
