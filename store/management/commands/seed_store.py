from django.core.management.base import BaseCommand
from django.db import transaction

from store.models import Category, Promotion, Review, SalesPoint
from store.services.processes import DemoCatalogGenerationTemplate
from store.services.proxy import ProductCatalogProxy


IMAGE_FIGURE = "https://images.unsplash.com/photo-1612036782180-6f0b6cd846fe?auto=format&fit=crop&w=900&q=80"
IMAGE_MANGA = "https://images.unsplash.com/photo-1613376023733-0a73315d9b06?auto=format&fit=crop&w=900&q=80"
IMAGE_CLOTHES = "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?auto=format&fit=crop&w=900&q=80"
IMAGE_POSTER = "https://images.unsplash.com/photo-1513475382585-d06e58bcb0ea?auto=format&fit=crop&w=900&q=80"
IMAGE_ACCESSORY = "https://images.unsplash.com/photo-1511499767150-a48a237f0083?auto=format&fit=crop&w=900&q=80"


CATEGORIES = [
    ("figures", "Фигурки", "", "Коллекционные фигурки и статуэтки."),
    ("apparel", "Одежда", "", "Футболки, худи и косплейные вещи."),
    ("paper", "Манга и арт", "", "Манга, постеры и артбуки."),
    ("accessories", "Аксессуары", "", "Брелоки, значки, сумки и мелкая атрибутика."),
    ("scale-figures", "Scale-фигурки", "figures", "Детализированные фигурки для витрины."),
    ("nendoroid", "Nendoroid", "figures", "Компактные фигурки с сменными лицами."),
    ("hoodies", "Худи", "apparel", "Теплая одежда с аниме-принтами."),
    ("posters", "Постеры", "paper", "Плакаты для комнаты и рабочего места."),
]


PRODUCTS = [
    {"slug": "gojo-scale-figure", "category": "scale-figures", "merch_type": "figure", "name": "Фигурка Сатору Годжо 1/7", "anime_title": "Jujutsu Kaisen", "description": "Динамичная поза и прозрачная подставка с эффектом техники.", "price": "6490.00", "stock": 8, "rating": "4.90", "popularity_score": 98, "sales_count": 42, "image_url": IMAGE_FIGURE, "limited": True},
    {"slug": "makima-figure", "category": "scale-figures", "merch_type": "figure", "name": "Фигурка Макима офисная версия", "anime_title": "Chainsaw Man", "description": "Коллекционная фигурка с аккуратной покраской и сменной рукой.", "price": "5790.00", "stock": 6, "rating": "4.80", "popularity_score": 94, "sales_count": 35, "image_url": IMAGE_FIGURE},
    {"slug": "nezuko-nendoroid", "category": "nendoroid", "merch_type": "figure", "name": "Nendoroid Нэдзуко Камадо", "anime_title": "Demon Slayer", "description": "Компактная фигурка с несколькими выражениями лица.", "price": "4290.00", "stock": 11, "rating": "4.75", "popularity_score": 91, "sales_count": 30, "image_url": IMAGE_FIGURE, "gift_wrap": True},
    {"slug": "luffy-gear-five-figure", "category": "scale-figures", "merch_type": "figure", "name": "Фигурка Луффи Gear Five", "anime_title": "One Piece", "description": "Яркая фигурка с облачной подставкой и эффектом движения.", "price": "6990.00", "stock": 5, "rating": "4.95", "popularity_score": 97, "sales_count": 45, "image_url": IMAGE_FIGURE, "limited": True},
    {"slug": "levi-ackerman-figure", "category": "scale-figures", "merch_type": "figure", "name": "Фигурка Леви Аккерман", "anime_title": "Attack on Titan", "description": "Фигурка с плащом разведкорпуса и клинками УПМ.", "price": "6190.00", "stock": 4, "rating": "4.82", "popularity_score": 87, "sales_count": 27, "image_url": IMAGE_FIGURE},
    {"slug": "chainsaw-hoodie", "category": "hoodies", "merch_type": "clothes", "name": "Худи Chainsaw Man черное", "anime_title": "Chainsaw Man", "description": "Плотное худи с крупным принтом на спине.", "price": "3490.00", "stock": 18, "rating": "4.60", "popularity_score": 88, "sales_count": 31, "image_url": IMAGE_CLOTHES},
    {"slug": "gojo-hoodie", "category": "hoodies", "merch_type": "clothes", "name": "Худи Gojo Infinity", "anime_title": "Jujutsu Kaisen", "description": "Минималистичный дизайн с вышивкой на груди.", "price": "3690.00", "stock": 14, "rating": "4.70", "popularity_score": 90, "sales_count": 29, "image_url": IMAGE_CLOTHES},
    {"slug": "totoro-tshirt", "category": "apparel", "merch_type": "clothes", "name": "Футболка Totoro Forest", "anime_title": "My Neighbor Totoro", "description": "Светлая футболка с лесным принтом.", "price": "1890.00", "stock": 22, "rating": "4.55", "popularity_score": 74, "sales_count": 16, "image_url": IMAGE_CLOTHES},
    {"slug": "eva-tshirt", "category": "apparel", "merch_type": "clothes", "name": "Футболка EVA Unit-01", "anime_title": "Evangelion", "description": "Контрастный принт с силуэтом Евы-01.", "price": "2090.00", "stock": 17, "rating": "4.65", "popularity_score": 83, "sales_count": 23, "image_url": IMAGE_CLOTHES},
    {"slug": "demon-slayer-poster", "category": "posters", "merch_type": "poster", "name": "Постер Demon Slayer Hashira", "anime_title": "Demon Slayer", "description": "Постер с групповой композицией столпов.", "price": "790.00", "stock": 40, "rating": "4.45", "popularity_score": 84, "sales_count": 54, "image_url": IMAGE_POSTER},
    {"slug": "one-piece-poster", "category": "posters", "merch_type": "poster", "name": "Постер One Piece Wanted", "anime_title": "One Piece", "description": "Серия постеров в стиле объявлений о награде.", "price": "690.00", "stock": 36, "rating": "4.50", "popularity_score": 81, "sales_count": 50, "image_url": IMAGE_POSTER, "gift_wrap": True},
    {"slug": "spirited-away-poster", "category": "posters", "merch_type": "poster", "name": "Постер Spirited Away Bathhouse", "anime_title": "Spirited Away", "description": "Арт с вечерним видом на купальню.", "price": "890.00", "stock": 19, "rating": "4.85", "popularity_score": 79, "sales_count": 21, "image_url": IMAGE_POSTER},
    {"slug": "berserk-deluxe-one", "category": "paper", "merch_type": "manga", "name": "Манга Berserk Deluxe том 1", "anime_title": "Berserk", "description": "Твердое издание первого тома темного фэнтези.", "price": "2990.00", "stock": 9, "rating": "4.95", "popularity_score": 89, "sales_count": 24, "image_url": IMAGE_MANGA},
    {"slug": "one-piece-manga-one", "category": "paper", "merch_type": "manga", "name": "Манга One Piece том 1", "anime_title": "One Piece", "description": "Первый том приключений команды Соломенной шляпы.", "price": "990.00", "stock": 28, "rating": "4.80", "popularity_score": 86, "sales_count": 60, "image_url": IMAGE_MANGA},
    {"slug": "jujutsu-manga-zero", "category": "paper", "merch_type": "manga", "name": "Манга Jujutsu Kaisen 0", "anime_title": "Jujutsu Kaisen", "description": "Предыстория с Ютой Оккоцу и проклятием Рики.", "price": "1090.00", "stock": 25, "rating": "4.72", "popularity_score": 92, "sales_count": 58, "image_url": IMAGE_MANGA},
    {"slug": "anya-keychain", "category": "accessories", "merch_type": "accessory", "name": "Брелок Аня Форджер", "anime_title": "Spy x Family", "description": "Акриловый брелок с двусторонней печатью.", "price": "390.00", "stock": 55, "rating": "4.40", "popularity_score": 76, "sales_count": 47, "image_url": IMAGE_ACCESSORY},
    {"slug": "akatsuki-ring", "category": "accessories", "merch_type": "accessory", "name": "Кольцо Акацуки", "anime_title": "Naruto", "description": "Металлическое кольцо с красным символом.", "price": "590.00", "stock": 33, "rating": "4.35", "popularity_score": 73, "sales_count": 33, "image_url": IMAGE_ACCESSORY},
    {"slug": "sailor-moon-bag", "category": "accessories", "merch_type": "accessory", "name": "Сумка Sailor Moon Luna", "anime_title": "Sailor Moon", "description": "Небольшая сумка с вышивкой и регулируемым ремнем.", "price": "2490.00", "stock": 12, "rating": "4.68", "popularity_score": 78, "sales_count": 19, "image_url": IMAGE_ACCESSORY, "gift_wrap": True},
    {"slug": "naruto-headband", "category": "accessories", "merch_type": "accessory", "name": "Повязка Конохи", "anime_title": "Naruto", "description": "Тканевая повязка с металлической пластиной.", "price": "490.00", "stock": 44, "rating": "4.30", "popularity_score": 75, "sales_count": 41, "image_url": IMAGE_ACCESSORY},
    {"slug": "spy-family-poster", "category": "posters", "merch_type": "poster", "name": "Постер Spy x Family домашний вечер", "anime_title": "Spy x Family", "description": "Теплая композиция семьи Форджеров.", "price": "750.00", "stock": 31, "rating": "4.52", "popularity_score": 80, "sales_count": 38, "image_url": IMAGE_POSTER},
]


class Command(BaseCommand):
    help = "Заполняет магазин демо-категориями, товарами, отзывами и точками продаж."

    @transaction.atomic
    def handle(self, *args, **options):
        categories = {}
        for slug, name, parent_slug, description in CATEGORIES:
            parent = categories.get(parent_slug)
            category, _ = Category.objects.update_or_create(
                slug=slug,
                defaults={"name": name, "parent": parent, "description": description},
            )
            categories[slug] = category

        Promotion.objects.update_or_create(
            code="spring-fest",
            defaults={"name": "Весенний аниме-фест", "discount_percent": 12, "is_active": True},
        )

        generator = DemoCatalogGenerationTemplate()
        products = generator.generate(PRODUCTS, lambda slug: categories[slug])

        for index, product in enumerate(products, start=1):
            base = 4 + (index % 5)
            for week in range(1, 9):
                units = base + week + ((index * week) % 4)
                SalesPoint.objects.update_or_create(
                    product=product,
                    week_number=week,
                    defaults={"units_sold": units},
                )

            Review.objects.get_or_create(
                product=product,
                customer_name="Мика",
                defaults={"rating": 5, "text": "Качественная вещь, выглядит как на витрине."},
            )

        ProductCatalogProxy.clear_cache()
        self.stdout.write(self.style.SUCCESS(f"Готово: {len(products)} товаров и {SalesPoint.objects.count()} точек продаж."))
