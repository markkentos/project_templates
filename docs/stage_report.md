# Отчет по этапам

## Тема

Интернет-магазин аниме атрибутики `Anime Shelf`.

## Этап 1

1. Создано Django-приложение `store`.
2. БД SQLite описана моделями Django.
3. Базовое приложение запускается через `python manage.py runserver`.
4. BPMN находится в `docs/bpmn.md`; отражены процессы покупки и пополнения каталога, а также используемые таблицы БД.
5. Основные сущности: `Category`, `Product`, `Customer`, `Cart`, `CartItem`, `Order`, `OrderItem`, `Promotion`, `Review`, `SalesPoint`, `ProcessLog`.
6. Математическая модель: линейный тренд продаж `SalesTrendModel`, прогнозирует спрос следующей недели по точкам `SalesPoint`.
7. Паттерны этапа: стратегии цены и доставки, состояние заказа, синглтоны `StoreSettings`, `EventBus`, реестр стратегий.

## Этап 2

1. ERD находится в `docs/erd.md`.
2. БД создается миграциями Django.
3. Заполнение БД: `python manage.py seed_store`, создается 20 товаров и недельные точки продаж.
4. Шаблонный метод BPMN: `OrderProcessTemplate` и подкласс `StandardOrderProcess`.
5. Стратегии: `RegularPricingStrategy`, `OtakuClubPricingStrategy`, `PromoPricingStrategy`, `PickupShippingStrategy`, `CourierShippingStrategy`, `ExpressShippingStrategy`.
6. Математическая модель реализована в `store/services/math_models.py`.
7. Генерация товаров: абстрактная фабрика `AbstractMerchFactory` и декораторы `LimitedEditionDecorator`, `GiftWrapDecorator`.

## Этап 3

1. Диаграмма машины состояний находится в `docs/state_machine.md`.
2. Новый модуль трендов подключен через `AnimeTrendAdapter`.
3. Наблюдатель: `EventBus`, `ProcessLogObserver`, `NotificationObserver`, `LowStockObserver`.
4. Задачи выполняются через команды: `AddToCartCommand`, `UpdateCartItemCommand`, `CheckoutCommand`, `AdvanceOrderStateCommand`.
5. Генерация элементов через шаблонный метод: `ProductGenerationTemplate`, `DemoCatalogGenerationTemplate`.

## Этап 4

1. Оформлен UI: каталог, карточка товара, корзина, checkout, заказ, дерево каталога, страница паттернов.
2. Клиентская версия каталога развернута через заместитель `ProductCatalogProxy`.
3. Иерархия и перебор: `CategoryNode`, `ProductLeaf`, `CatalogIterator`.
4. Финальная диаграмма классов находится в `docs/class_diagram.md`.

## Этап 5

1. Презентация-аналог PowerPoint: `presentation/index.html`.
2. Рассказ для защиты и электронная доска: `presentation/defense_speech.md`, `presentation/electronic_board.md`.
3. Use Case: `docs/use_case.md`.
