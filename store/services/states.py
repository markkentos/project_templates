from dataclasses import dataclass

from store.models import Order

from .observers import DomainEvent, configure_default_observers


@dataclass(frozen=True)
class Transition:
    action: str
    target: str
    label: str


class OrderState:
    status = ""
    transitions: tuple[Transition, ...] = ()

    def allowed_transitions(self):
        return self.transitions


class CreatedState(OrderState):
    status = Order.Status.CREATED
    transitions = (
        Transition("pay", Order.Status.PAID, "Оплатить"),
        Transition("cancel", Order.Status.CANCELLED, "Отменить"),
    )


class PaidState(OrderState):
    status = Order.Status.PAID
    transitions = (
        Transition("pack", Order.Status.PACKED, "Упаковать"),
        Transition("cancel", Order.Status.CANCELLED, "Отменить"),
    )


class PackedState(OrderState):
    status = Order.Status.PACKED
    transitions = (Transition("ship", Order.Status.SHIPPED, "Отправить"),)


class ShippedState(OrderState):
    status = Order.Status.SHIPPED
    transitions = (Transition("deliver", Order.Status.DELIVERED, "Доставить"),)


class DeliveredState(OrderState):
    status = Order.Status.DELIVERED
    transitions = ()


class CancelledState(OrderState):
    status = Order.Status.CANCELLED
    transitions = ()


class OrderStateMachine:
    states = {
        Order.Status.CREATED: CreatedState(),
        Order.Status.PAID: PaidState(),
        Order.Status.PACKED: PackedState(),
        Order.Status.SHIPPED: ShippedState(),
        Order.Status.DELIVERED: DeliveredState(),
        Order.Status.CANCELLED: CancelledState(),
    }

    def get_state(self, order):
        return self.states[order.status]

    def allowed_transitions(self, order):
        return self.get_state(order).allowed_transitions()

    def apply(self, order, action):
        transition = next(
            (item for item in self.allowed_transitions(order) if item.action == action),
            None,
        )
        if transition is None:
            raise ValueError(f"Переход '{action}' недоступен для статуса '{order.get_status_display()}'.")

        old_status = order.get_status_display()
        order.status = transition.target
        order.save(update_fields=["status", "updated_at"])

        configure_default_observers().publish(
            DomainEvent(
                event_type="order.status_changed",
                order_id=order.pk,
                message=f"Заказ #{order.pk}: {old_status} -> {order.get_status_display()}",
            )
        )
        return order
