from abc import ABC, abstractmethod
from copy import deepcopy
from decimal import Decimal


class AbstractMerchFactory(ABC):
    merch_type = ""

    @abstractmethod
    def create_product_data(self, row):
        raise NotImplementedError

    def base_payload(self, row):
        return {
            "name": row["name"],
            "anime_title": row["anime_title"],
            "description": row["description"],
            "price": Decimal(row["price"]),
            "stock": row["stock"],
            "rating": Decimal(row.get("rating", "4.70")),
            "popularity_score": row.get("popularity_score", 70),
            "sales_count": row.get("sales_count", 0),
            "image_url": row.get("image_url", ""),
            "merch_type": self.merch_type,
        }


class FigureFactory(AbstractMerchFactory):
    merch_type = "figure"

    def create_product_data(self, row):
        payload = self.base_payload(row)
        payload["description"] += " Подходит для коллекционной полки и витрины."
        return payload


class ApparelFactory(AbstractMerchFactory):
    merch_type = "clothes"

    def create_product_data(self, row):
        payload = self.base_payload(row)
        payload["description"] += " Мягкая ткань и принт, рассчитанный на ежедневную носку."
        return payload


class PrintFactory(AbstractMerchFactory):
    merch_type = "poster"

    def create_product_data(self, row):
        payload = self.base_payload(row)
        payload["description"] += " Плотная бумага, насыщенная печать, формат A2."
        return payload


class MangaFactory(AbstractMerchFactory):
    merch_type = "manga"

    def create_product_data(self, row):
        payload = self.base_payload(row)
        payload["description"] += " Коллекционное издание с качественной обложкой."
        return payload


class AccessoryFactory(AbstractMerchFactory):
    merch_type = "accessory"

    def create_product_data(self, row):
        payload = self.base_payload(row)
        payload["description"] += " Маленькая деталь для повседневного образа фаната."
        return payload


class ProductDataDecorator:
    def __init__(self, payload):
        self.payload = deepcopy(payload)

    def decorate(self):
        return self.payload


class LimitedEditionDecorator(ProductDataDecorator):
    def decorate(self):
        payload = super().decorate()
        payload["name"] = f"Limited Edition: {payload['name']}"
        payload["price"] = (payload["price"] * Decimal("1.18")).quantize(Decimal("0.01"))
        payload["description"] += " Ограниченный тираж с номерным сертификатом."
        payload["popularity_score"] += 12
        return payload


class GiftWrapDecorator(ProductDataDecorator):
    def decorate(self):
        payload = super().decorate()
        payload["description"] += " В комплект входит подарочная упаковка."
        payload["price"] = (payload["price"] + Decimal("250.00")).quantize(Decimal("0.01"))
        return payload


class MerchFactoryProvider:
    """Паттерн Фабричный метод для создания объектов фабрик."""

    @staticmethod
    def get_factory(merch_type) -> AbstractMerchFactory:
        factories = {
            "figure": FigureFactory(),
            "clothes": ApparelFactory(),
            "poster": PrintFactory(),
            "manga": MangaFactory(),
            "accessory": AccessoryFactory(),
        }
        if merch_type not in factories:
            raise ValueError(f"Неизвестный тип товара: {merch_type}")
        return factories[merch_type]


def factory_for_merch_type(merch_type):
    return MerchFactoryProvider.get_factory(merch_type)

