from dataclasses import dataclass, field
from typing import Any

from .singletons import SingletonMeta, StoreSettings


@dataclass(frozen=True)
class DomainEvent:
    event_type: str
    message: str
    order_id: int | None = None
    level: str = "info"
    payload: dict[str, Any] = field(default_factory=dict)


class Observer:
    def update(self, event):
        raise NotImplementedError


class EventBus(metaclass=SingletonMeta):
    def __init__(self):
        self._observers = {}

    def subscribe(self, event_type, observer):
        observers = self._observers.setdefault(event_type, [])
        if observer not in observers:
            observers.append(observer)

    def publish(self, event):
        for observer in self._observers.get(event.event_type, []):
            observer.update(event)
        for observer in self._observers.get("*", []):
            observer.update(event)


class ProcessLogObserver(Observer):
    def update(self, event):
        from store.models import Order, ProcessLog

        order = Order.objects.filter(pk=event.order_id).first() if event.order_id else None
        ProcessLog.objects.create(
            order=order,
            event_type=event.event_type,
            level=event.level,
            message=event.message,
        )

    def __eq__(self, other):
        return isinstance(other, ProcessLogObserver)


class LowStockObserver(Observer):
    def update(self, event):
        if event.event_type != "order.created":
            return

        from store.models import Order, ProcessLog

        order = Order.objects.filter(pk=event.order_id).prefetch_related("items__product").first()
        if not order:
            return

        settings = StoreSettings()
        for item in order.items.all():
            if item.product.stock <= settings.low_stock_threshold:
                ProcessLog.objects.create(
                    order=order,
                    event_type="stock.low",
                    level="warning",
                    message=f"Товар '{item.product.name}' скоро закончится: осталось {item.product.stock}.",
                )

    def __eq__(self, other):
        return isinstance(other, LowStockObserver)


class NotificationObserver(Observer):
    def update(self, event):
        if event.event_type not in {"order.created", "order.status_changed"}:
            return

        from store.models import Order, ProcessLog

        order = Order.objects.filter(pk=event.order_id).first() if event.order_id else None
        ProcessLog.objects.create(
            order=order,
            event_type="notification.sent",
            level="info",
            message=f"Имитация отправки уведомления: {event.message}",
        )

    def __eq__(self, other):
        return isinstance(other, NotificationObserver)


def configure_default_observers():
    bus = EventBus()
    bus.subscribe("*", ProcessLogObserver())
    bus.subscribe("order.created", LowStockObserver())
    bus.subscribe("order.created", NotificationObserver())
    bus.subscribe("order.status_changed", NotificationObserver())
    return bus
