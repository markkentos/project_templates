from dataclasses import dataclass
from decimal import Decimal

from .singletons import SingletonMeta, StoreSettings


@dataclass(frozen=True)
class PriceBreakdown:
    subtotal: Decimal
    discount: Decimal
    total: Decimal
    label: str


class PricingStrategy:
    code = "base"
    label = "Базовая цена"

    def calculate(self, subtotal):
        raise NotImplementedError


class RegularPricingStrategy(PricingStrategy):
    code = "regular"
    label = "Без скидки"

    def calculate(self, subtotal):
        subtotal = StoreSettings().money(subtotal)
        return PriceBreakdown(subtotal, Decimal("0.00"), subtotal, self.label)


class OtakuClubPricingStrategy(PricingStrategy):
    code = "otaku"
    label = "Клуб отаку: -10%"

    def calculate(self, subtotal):
        settings = StoreSettings()
        subtotal = settings.money(subtotal)
        discount = settings.money(subtotal * settings.otaku_club_discount)
        return PriceBreakdown(subtotal, discount, subtotal - discount, self.label)


class PromoPricingStrategy(PricingStrategy):
    code = "promo"
    label = "Сезонная промоакция"

    def calculate(self, subtotal):
        from store.models import Promotion

        settings = StoreSettings()
        subtotal = settings.money(subtotal)
        promotion = Promotion.objects.filter(is_active=True).order_by("-discount_percent").first()
        percent = Decimal(promotion.discount_percent if promotion else 5) / Decimal("100")
        discount = settings.money(subtotal * percent)
        label = f"{self.label}: -{int(percent * 100)}%"
        return PriceBreakdown(subtotal, discount, subtotal - discount, label)


class PricingStrategyRegistry(metaclass=SingletonMeta):
    def __init__(self):
        self._strategies = {
            RegularPricingStrategy.code: RegularPricingStrategy(),
            OtakuClubPricingStrategy.code: OtakuClubPricingStrategy(),
            PromoPricingStrategy.code: PromoPricingStrategy(),
        }

    def get(self, code):
        return self._strategies.get(code, self._strategies[RegularPricingStrategy.code])

    def choices(self):
        return [(strategy.code, strategy.label) for strategy in self._strategies.values()]

    def all(self):
        return list(self._strategies.values())


def get_pricing_strategy(code):
    return PricingStrategyRegistry().get(code)


def pricing_choices():
    return PricingStrategyRegistry().choices()
