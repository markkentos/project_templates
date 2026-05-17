from dataclasses import dataclass, field

from store.models import Category


class CatalogComponent:
    kind = "component"

    def render_label(self):
        raise NotImplementedError

    def iter_items(self):
        yield self


@dataclass
class ProductLeaf(CatalogComponent):
    kind = "product"
    product: object
    level: int = 0

    def render_label(self):
        return f"{self.product.name} - {self.product.price} руб."

    @property
    def indent(self):
        return self.level * 24


@dataclass
class CategoryNode(CatalogComponent):
    kind = "category"
    category: object
    level: int = 0
    children: list[CatalogComponent] = field(default_factory=list)

    def add(self, component):
        self.children.append(component)

    def render_label(self):
        return self.category.name

    @property
    def indent(self):
        return self.level * 24

    def iter_items(self):
        yield self
        for child in self.children:
            yield from child.iter_items()


class CatalogIterator:
    def __init__(self, roots):
        self._items = []
        for root in roots:
            self._items.extend(root.iter_items())
        self._index = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self._index >= len(self._items):
            raise StopIteration
        item = self._items[self._index]
        self._index += 1
        return item


def build_catalog_tree():
    categories = Category.objects.prefetch_related("products", "children").all()
    by_parent = {}
    for category in categories:
        by_parent.setdefault(category.parent_id, []).append(category)

    def build_node(category, level=0):
        node = CategoryNode(category=category, level=level)
        for child in by_parent.get(category.id, []):
            node.add(build_node(child, level + 1))
        for product in category.products.filter(is_active=True).order_by("name"):
            node.add(ProductLeaf(product=product, level=level + 1))
        return node

    return [build_node(category) for category in by_parent.get(None, [])]
