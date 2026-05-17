from dataclasses import dataclass
from decimal import Decimal

from .singletons import SingletonMeta, StoreSettings


@dataclass(frozen=True)
class ShippingBreakdown:
    method: str
    label: str
    price: Decimal
    days: str


class ShippingStrategy:
    code = "base"
    label = "Доставка"
    days = "2-5 дней"

    def calculate(self, subtotal):
        raise NotImplementedError


class PickupShippingStrategy(ShippingStrategy):
    code = "pickup"
    label = "Самовывоз из шоурума"
    days = "сегодня"

    def calculate(self, subtotal):
        return ShippingBreakdown(self.code, self.label, Decimal("0.00"), self.days)


class CourierShippingStrategy(ShippingStrategy):
    code = "courier"
    label = "Курьер по городу"
    days = "1-2 дня"

    def calculate(self, subtotal):
        settings = StoreSettings()
        price = Decimal("0.00") if subtotal >= settings.free_shipping_threshold else Decimal("390.00")
        return ShippingBreakdown(self.code, self.label, price, self.days)


class ExpressShippingStrategy(ShippingStrategy):
    code = "express"
    label = "Экспресс-доставка"
    days = "завтра"

    def calculate(self, subtotal):
        settings = StoreSettings()
        price = Decimal("590.00") if subtotal >= settings.free_shipping_threshold else Decimal("890.00")
        return ShippingBreakdown(self.code, self.label, price, self.days)


class ShippingStrategyRegistry(metaclass=SingletonMeta):
    def __init__(self):
        self._strategies = {
            PickupShippingStrategy.code: PickupShippingStrategy(),
            CourierShippingStrategy.code: CourierShippingStrategy(),
            ExpressShippingStrategy.code: ExpressShippingStrategy(),
        }

    def get(self, code):
        return self._strategies.get(code, self._strategies[CourierShippingStrategy.code])

    def choices(self):
        return [(strategy.code, strategy.label) for strategy in self._strategies.values()]

    def all(self):
        return list(self._strategies.values())


def get_shipping_strategy(code):
    return ShippingStrategyRegistry().get(code)


def shipping_choices():
    return ShippingStrategyRegistry().choices()
