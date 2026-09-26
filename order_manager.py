import os
import uuid
import httpx
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional


@dataclass
class Order:
    id: str
    customer_phone: str
    items: List[dict]
    status: str = "received"
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    total: float = 0.0
    notes: str = ""

    def __post_init__(self):
        if not self.total:
            self.total = sum(item["price"] * item["qty"] for item in self.items)

    @property
    def status_emoji(self) -> str:
        return {
            "received": "ð¥",
            "confirmed": "â",
            "preparing": "ð¨âð³",
            "ready": "ð",
            "delivered": "ð",
            "cancelled": "â",
        }.get(self.status, "ð")

    def status_message(self) -> str:
        messages = {
            "received": "We've received your order and will confirm shortly.",
            "confirmed": "Your order is confirmed and going to the kitchen!",
            "preparing": "Our kitchen is preparing your delicious food.",
            "ready": "Your order is ready! It will be delivered soon.",
            "delivered": "Order delivered. Enjoy your meal! ð",
            "cancelled": "Your order has been cancelled.",
        }
        return messages.get(self.status, "Status updated.")


class OrderManager:
    def __init__(self):
        self._orders: dict[str, Order] = {}  # order_id -> Order
        self._kitchen_webhook = os.getenv("KITCHEN_WEBHOOK_URL", "")

    def create_order(self, customer_phone: str, items: List[dict], notes: str = "") -> Order:
        order_id = str(uuid.uuid4())[:8].upper()
        order = Order(
            id=order_id,
            customer_phone=customer_phone,
            items=items,
            notes=notes,
        )
        self._orders[order_id] = order
        self._notify_kitchen(order)
        return order

    def get_order(self, order_id: str) -> Optional[Order]:
        return self._orders.get(order_id)

    def get_active_orders(self, customer_phone: str) -> List[Order]:
        terminal_statuses = {"delivered", "cancelled"}
        return [
            o for o in self._orders.values()
            if o.customer_phone == customer_phone and o.status not in terminal_statuses
        ]

    def get_all_orders(self) -> List[Order]:
        return list(self._orders.values())

    def update_status(self, order_id: str, new_status: str) -> Optional[Order]:
        order = self._orders.get(order_id)
        if order:
            order.status = new_status
        return order

    def cancel_order(self, order_id: str) -> bool:
        order = self._orders.get(order_id)
        if order and order.status in {"received", "confirmed"}:
            order.status = "cancelled"
            return True
        return False

    def _notify_kitchen(self, order: Order):
        """Send order to kitchen dashboard via webhook."""
        if not self._kitchen_webhook:
            return
        try:
            payload = {
                "order_id": order.id,
                "customer_phone": order.customer_phone,
                "items": order.items,
                "total": order.total,
                "notes": order.notes,
                "created_at": order.created_at,
            }
            with httpx.Client(timeout=5) as client:
                client.post(self._kitchen_webhook, json=payload)
        except Exception as e:
            print(f"[OrderManager] Kitchen notification failed: {e}")

    def format_receipt(self, order: Order) -> str:
        lines = [f"*Order #{order.id}*\n"]
        for item in order.items:
            lines.append(f"  â¢ {item['name']} x{item['qty']} = PKR {item['price'] * item['qty']}")
        lines.append(f"\n*Total: PKR {order.total:.0f}*")
        if order.notes:
            lines.append(f"Notes: {order.notes}")
        return "\n".join(lines)
