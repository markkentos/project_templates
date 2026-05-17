from decimal import Decimal


class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class StoreSettings(metaclass=SingletonMeta):
    """Единая конфигурация бизнес-правил магазина."""

    brand_name = "Anime Shelf"
    free_shipping_threshold = Decimal("7000.00")
    otaku_club_discount = Decimal("0.10")
    premium_packaging_price = Decimal("350.00")
    low_stock_threshold = 3

    def money(self, value):
        return Decimal(value).quantize(Decimal("0.01"))
