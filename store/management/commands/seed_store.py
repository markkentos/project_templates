from decimal import Decimal
from django.core.management.base import BaseCommand
from django.db import transaction
from django.contrib.auth.models import User

from store.models import Category, Product, Customer, Cart, CartItem, Promotion, Order, OrderItem, Review, SalesPoint, ProcessLog
from store.services.processes import DemoCatalogGenerationTemplate
from store.services.proxy import ProductCatalogProxy

# Локальные оффлайн-векторные SVG-изображения
IMAGE_FIGURE = "/static/store/images/figure.svg"
IMAGE_CLOTHES = "/static/store/images/clothes.svg"
IMAGE_POSTER = "/static/store/images/poster.svg"
IMAGE_MANGA = "/static/store/images/manga.svg"
IMAGE_ACCESSORY = "/static/store/images/accessory.svg"

# 10 категорий (Этап 2: минимум 10 записей)
CATEGORIES = [
    ("figures", "Фигурки", None, "Коллекционные фигурки и статуэтки."),
    ("apparel", "Одежда", None, "Футболки, худи и косплейные вещи."),
    ("paper", "Манга и арт", None, "Манга, постеры и артбуки."),
    ("accessories", "Аксессуары", None, "Брелоки, значки, сумки и мелкая атрибутика."),
    ("scale-figures", "Scale-фигурки", "figures", "Детализированные масштабные фигурки."),
    ("nendoroid", "Nendoroid", "figures", "Компактные чиби-фигурки с аксессуарами."),
    ("hoodies", "Худи и свитшоты", "apparel", "Теплая одежда с качественными принтами."),
    ("posters", "Постеры и плакаты", "paper", "Настенные арты и плакаты форматов A2/A3."),
    ("plushies", "Плюшевые игрушки", "accessories", "Мягкие аниме-игрушки и маскоты."),
    ("keychains", "Брелоки и значки", "accessories", "Металлическая и акриловая мелочь на ключи."),
]

# 20 товаров с локальными оффлайн SVG
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
    {"slug": "anya-keychain", "category": "keychains", "merch_type": "accessory", "name": "Брелок Аня Форджер акрил", "anime_title": "Spy x Family", "description": "Акриловый брелок с двусторонней печатью.", "price": "390.00", "stock": 55, "rating": "4.40", "popularity_score": 76, "sales_count": 47, "image_url": IMAGE_ACCESSORY},
    {"slug": "akatsuki-ring", "category": "accessories", "merch_type": "accessory", "name": "Кольцо Акацуки", "anime_title": "Naruto", "description": "Металлическое кольцо с красным символом членов Акацуки.", "price": "590.00", "stock": 33, "rating": "4.35", "popularity_score": 73, "sales_count": 33, "image_url": IMAGE_ACCESSORY},
    {"slug": "sailor-moon-bag", "category": "accessories", "merch_type": "accessory", "name": "Сумка Sailor Moon Luna", "anime_title": "Sailor Moon", "description": "Небольшая сумка с вышивкой и регулируемым ремнем.", "price": "2490.00", "stock": 12, "rating": "4.68", "popularity_score": 78, "sales_count": 19, "image_url": IMAGE_ACCESSORY, "gift_wrap": True},
    {"slug": "naruto-headband", "category": "accessories", "merch_type": "accessory", "name": "Повязка Конохи", "anime_title": "Naruto", "description": "Тканевая повязка с металлической пластиной скрытого листа.", "price": "490.00", "stock": 44, "rating": "4.30", "popularity_score": 75, "sales_count": 41, "image_url": IMAGE_ACCESSORY},
    {"slug": "spy-family-poster", "category": "posters", "merch_type": "poster", "name": "Постер Spy x Family домашний вечер", "anime_title": "Spy x Family", "description": "Теплая композиция семьи Форджеров.", "price": "750.00", "stock": 31, "rating": "4.52", "popularity_score": 80, "sales_count": 38, "image_url": IMAGE_POSTER},
]

# 10 покупателей
CUSTOMERS = [
    {"name": "Иван Ivanov", "email": "ivan@example.com", "phone": "+79991112233", "city": "Москва"},
    {"name": "Алена Смирнова", "email": "alena@example.com", "phone": "+79992223344", "city": "Санкт-Петербург"},
    {"name": "Дмитрий Петров", "email": "dima@example.com", "phone": "+79993334455", "city": "Новосибирск"},
    {"name": "Ольга Соколова", "email": "olga@example.com", "phone": "+79994445566", "city": "Екатеринбург"},
    {"name": "Сергей Морозов", "email": "sergey@example.com", "phone": "+79995556677", "city": "Казань"},
    {"name": "Анна Новикова", "email": "anna@example.com", "phone": "+79996667788", "city": "Нижний Новгород"},
    {"name": "Алексей Федоров", "email": "alex@example.com", "phone": "+79997778899", "city": "Челябинск"},
    {"name": "Мария Козлова", "email": "maria@example.com", "phone": "+79998889900", "city": "Самара"},
    {"name": "Павел Лебедев", "email": "pavel@example.com", "phone": "+79999990011", "city": "Ростов-на-Дону"},
    {"name": "Елена Васильева", "email": "elena_v@example.com", "phone": "+79990001122", "city": "Уфа"},
]

# 10 промоакций
PROMOTIONS = [
    {"name": "Весенний аниме-фест", "code": "spring-fest", "discount_percent": 12, "is_active": True},
    {"name": "Скидка первокурсника", "code": "freshman", "discount_percent": 10, "is_active": True},
    {"name": "Летний гик-фестиваль", "code": "summer-fest", "discount_percent": 15, "is_active": False},
    {"name": "Клуб отаку: промо", "code": "otaku-promo", "discount_percent": 10, "is_active": True},
    {"name": "День рождения магазина", "code": "store-bday", "discount_percent": 20, "is_active": True},
    {"name": "Черная пятница", "code": "black-friday", "discount_percent": 25, "is_active": False},
    {"name": "Новогодняя распродажа", "code": "new-year", "discount_percent": 15, "is_active": True},
    {"name": "Киберпонедельник", "code": "cyber", "discount_percent": 18, "is_active": False},
    {"name": "Хэллоуин-скидка", "code": "halloween", "discount_percent": 13, "is_active": True},
    {"name": "Скидка для друзей", "code": "friends", "discount_percent": 5, "is_active": True},
]


class Command(BaseCommand):
    help = "Заполняет магазин демо-данными в полном объеме (минимум 10 записей во всех 11 таблицах)."

    @transaction.atomic
    def handle(self, *args, **options):
        # Очистка таблиц перед заполнением
        SalesPoint.objects.all().delete()
        Review.objects.all().delete()
        OrderItem.objects.all().delete()
        ProcessLog.objects.all().delete()
        Order.objects.all().delete()
        CartItem.objects.all().delete()
        Cart.objects.all().delete()
        Promotion.objects.all().delete()
        Product.objects.all().delete()
        Customer.objects.all().delete()
        Category.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()

        # 1. Заполнение Категорий (10 штук)
        categories_dict = {}
        for slug, name, parent_slug, description in CATEGORIES:
            parent = categories_dict.get(parent_slug)
            category = Category.objects.create(
                slug=slug,
                name=name,
                parent=parent,
                description=description,
            )
            categories_dict[slug] = category

        # 2. Заполнение Промоакций (10 штук)
        for promo in PROMOTIONS:
            Promotion.objects.create(**promo)

        # 3. Заполнение Товаров (20 штук)
        generator = DemoCatalogGenerationTemplate()
        products = generator.generate(PRODUCTS, lambda slug: categories_dict[slug])

        # 4. Заполнение Пользователей и Покупателей (10 штук)
        seeded_customers = []
        for i, cust in enumerate(CUSTOMERS, start=1):
            username = f"customer{i}"
            user = User.objects.create_user(
                username=username,
                email=cust["email"],
                password="customer123",
                is_staff=False
            )
            customer = Customer.objects.create(
                user=user,
                name=cust["name"],
                email=cust["email"],
                phone=cust["phone"],
                city=cust["city"]
            )
            seeded_customers.append(customer)

        # Создание Менеджеров (10 штук)
        for i in range(1, 11):
            User.objects.create_user(
                username=f"manager{i}",
                email=f"manager{i}@example.com",
                password="manager123",
                is_staff=True
            )

        # 5. Заполнение Корзин и Позиций корзин (10 штук)
        for i in range(1, 11):
            cart = Cart.objects.create(
                session_key=f"seeded_session_key_{i}",
                status=Cart.Status.CHECKED_OUT if i % 2 == 0 else Cart.Status.OPEN
            )
            # В каждую корзину добавим по 1-2 товара
            p1 = products[i % len(products)]
            CartItem.objects.create(cart=cart, product=p1, quantity=(i % 3) + 1)
            if i % 3 == 0:
                p2 = products[(i + 3) % len(products)]
                CartItem.objects.create(cart=cart, product=p2, quantity=1)
        # 6. Заполнение Заказов и Позиций заказов (10 штук в разных состояниях)

        order_statuses = [
            Order.Status.CREATED,
            Order.Status.PAID,
            Order.Status.PACKED,
            Order.Status.SHIPPED,
            Order.Status.DELIVERED,
            Order.Status.CANCELLED,
            Order.Status.CREATED,
            Order.Status.PAID,
            Order.Status.PACKED,
            Order.Status.SHIPPED,
        ]
        
        for i, customer in enumerate(seeded_customers, start=1):
            status = order_statuses[i - 1]
            order = Order.objects.create(
                customer=customer,
                status=status,
                delivery_method="courier" if i % 2 == 0 else "pickup",
                pricing_strategy="regular" if i % 3 == 0 else "otaku",
                comment=f"Демонстрационный заказ №{i}. Статус: {status}."
            )
            
            # Позиции заказа
            p1 = products[(i * 2) % len(products)]
            OrderItem.objects.create(
                order=order,
                product=p1,
                product_name=p1.name,
                unit_price=p1.price,
                quantity=1
            )
            
            p2 = products[(i * 2 + 1) % len(products)]
            OrderItem.objects.create(
                order=order,
                product=p2,
                product_name=p2.name,
                unit_price=p2.price,
                quantity=2
            )
            
            # Расчет сумм заказа
            subtotal = p1.price + (p2.price * 2)
            discount = subtotal * Decimal("0.10") if order.pricing_strategy == "otaku" else Decimal("0.00")
            shipping_price = Decimal("390.00") if order.delivery_method == "courier" else Decimal("0.00")
            
            order.subtotal = subtotal
            order.discount = discount.quantize(Decimal("0.01"))
            order.shipping_price = shipping_price
            order.total = (subtotal - discount + shipping_price).quantize(Decimal("0.01"))
            order.save()

            # 7. Заполнение Системного Журнала (ProcessLog - минимум 10 записей)
            ProcessLog.objects.create(
                order=order,
                event_type="order.created",
                level=ProcessLog.Level.INFO,
                message=f"Заказ #{order.id} создан для {customer.name} на сумму {order.total} руб."
            )
            if status != Order.Status.CREATED:
                ProcessLog.objects.create(
                    order=order,
                    event_type="order.status_changed",
                    level=ProcessLog.Level.INFO,
                    message=f"Заказ #{order.id}: Статус изменен на '{order.get_status_display()}'."
                )

        # 8. Заполнение Отзывов (минимум 10 штук)
        reviewer_names = ["Мика", "Рин", "Такаши", "Кенджи", "Асука", "Синдзи", "Харука", "Нацуми", "Юки", "Акира"]
        review_texts = [
            "Качественная вещь, очень доволен!",
            "Упаковано супер, коробка целая.",
            "Печать яркая, цвета насыщенные.",
            "Заказал в подарок, получатель в восторге.",
            "Доставка быстрая, фигурка супердетализированная.",
            "Качество ткани отличное, принт мягкий.",
            "Том пришел без замятий, коллекционка!",
            "Размер подошел идеально, рекомендую.",
            "Красивый брелок, качественный акрил.",
            "Один из лучших товаров в моей коллекции!"
        ]
        
        for i in range(15):
            product = products[i % len(products)]
            Review.objects.create(
                product=product,
                customer_name=reviewer_names[i % len(reviewer_names)],
                rating=(i % 2) + 4,  # Оценки 4 и 5
                text=review_texts[i % len(review_texts)]
            )

        # 9. Заполнение Точек Продаж (SalesPoint - 160 записей)
        for index, product in enumerate(products, start=1):
            base = 4 + (index % 5)
            for week in range(1, 9):
                units = base + week + ((index * week) % 4)
                SalesPoint.objects.create(
                    product=product,
                    week_number=week,
                    units_sold=units,
                )

        ProductCatalogProxy.clear_cache()
        self.stdout.write(self.style.SUCCESS(
            f"Успешное заполнение БД:\n"
            f"- {Category.objects.count()} категорий\n"
            f"- {Product.objects.count()} товаров\n"
            f"- {Promotion.objects.count()} промоакций\n"
            f"- {Customer.objects.count()} покупателей\n"
            f"- {Cart.objects.count()} корзин ({CartItem.objects.count()} позиций)\n"
            f"- {Order.objects.count()} заказов ({OrderItem.objects.count()} позиций)\n"
            f"- {Review.objects.count()} отзывов\n"
            f"- {SalesPoint.objects.count()} точек продаж\n"
            f"- {ProcessLog.objects.count()} записей системного лога\n"
            f"Все таблицы базы данных наполнены (минимум по 10 записей)!"
        ))
