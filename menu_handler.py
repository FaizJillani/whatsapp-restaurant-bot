import os
import json
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class MenuItem:
    id: str
    name: str
    category: str
    price: float
    description: str = ""
    available: bool = True
    customizations: List[str] = field(default_factory=list)


DEFAULT_MENU = [
    # Starters
    {"id": "s1", "name": "Chicken Wings", "category": "starters", "price": 650, "description": "Crispy fried wings with dipping sauce", "customizations": ["Extra Spicy", "BBQ Sauce", "Garlic Butter"]},
    {"id": "s2", "name": "Loaded Fries", "category": "starters", "price": 450, "description": "Fries topped with cheese, jalapeÃ±os & sour cream", "customizations": ["Extra Cheese", "No JalapeÃ±os"]},
    {"id": "s3", "name": "Soup of the Day", "category": "starters", "price": 350, "description": "Chef's daily soup selection"},
    {"id": "s4", "name": "Spring Rolls", "category": "starters", "price": 400, "description": "Crispy vegetable spring rolls, 6 pieces"},
    {"id": "s5", "name": "Garlic Bread", "category": "starters", "price": 280, "description": "Toasted garlic bread with herb butter"},

    # Mains
    {"id": "m1", "name": "Chicken Biryani", "category": "mains", "price": 750, "description": "Fragrant basmati rice with spiced chicken", "customizations": ["Extra Raita", "Less Spice", "Extra Masala"]},
    {"id": "m2", "name": "Beef Burger", "category": "mains", "price": 850, "description": "Quarter pound beef patty with fries", "customizations": ["No Onion", "Extra Cheese", "Double Patty +200"]},
    {"id": "m3", "name": "Grilled Chicken", "category": "mains", "price": 950, "description": "Herb marinated grilled chicken with salad & rice"},
    {"id": "m4", "name": "Pasta Arrabiata", "category": "mains", "price": 700, "description": "Penne in spicy tomato sauce", "customizations": ["Add Chicken +150", "Extra Cheese", "Less Spicy"]},
    {"id": "m5", "name": "Fish & Chips", "category": "mains", "price": 1100, "description": "Beer battered fish fillet with fries & tartar sauce"},
    {"id": "m6", "name": "Mutton Karahi", "category": "mains", "price": 1400, "description": "Slow cooked mutton in tomato-based gravy", "customizations": ["Extra Naan", "Mild Spice"]},
    {"id": "m7", "name": "Vegetable Platter", "category": "mains", "price": 600, "description": "Seasonal grilled vegetables with hummus"},

    # Drinks & Desserts
    {"id": "d1", "name": "Mango Shake", "category": "drinks", "price": 300, "description": "Fresh mango blended with milk"},
    {"id": "d2", "name": "Fresh Lime Soda", "category": "drinks", "price": 200, "description": "Sparkling lime with mint"},
    {"id": "d3", "name": "Cold Coffee", "category": "drinks", "price": 280, "description": "Iced blended coffee with cream"},
    {"id": "d4", "name": "Chocolate Lava Cake", "category": "drinks", "price": 450, "description": "Warm chocolate cake with vanilla ice cream"},
    {"id": "d5", "name": "Gulab Jamun", "category": "drinks", "price": 280, "description": "4 pieces in sugar syrup"},
    {"id": "d6", "name": "Soft Drinks", "category": "drinks", "price": 150, "description": "Coke, Pepsi, Sprite, 7UP"},
]


class MenuHandler:
    def __init__(self):
        self._menu: List[MenuItem] = []
        self._load_menu()

    def _load_menu(self):
        menu_file = os.getenv("MENU_FILE", "")
        if menu_file and os.path.exists(menu_file):
            with open(menu_file) as f:
                data = json.load(f)
        else:
            data = DEFAULT_MENU

        self._menu = [MenuItem(**item) for item in data]

    def get_categories(self) -> List[str]:
        return list(dict.fromkeys(item.category for item in self._menu if item.available))

    def get_items_by_category(self, category: str) -> List[MenuItem]:
        return [item for item in self._menu if item.category == category and item.available]

    def get_item(self, item_id: str) -> Optional[MenuItem]:
        return next((item for item in self._menu if item.id == item_id and item.available), None)

    def search(self, query: str) -> List[MenuItem]:
        query_lower = query.lower()
        return [
            item for item in self._menu
            if item.available and (
                query_lower in item.name.lower() or
                query_lower in item.description.lower() or
                query_lower in item.category.lower()
            )
        ]

    def get_all_available(self) -> List[MenuItem]:
        return [item for item in self._menu if item.available]

    def format_menu_text(self) -> str:
        """Generate plain text menu for display."""
        lines = []
        for category in self.get_categories():
            lines.append(f"\n*{category.upper()}*")
            for item in self.get_items_by_category(category):
                lines.append(f"  â¢ {item.name} â PKR {item.price}")
                if item.description:
                    lines.append(f"    _{item.description}_")
        return "\n".join(lines)
