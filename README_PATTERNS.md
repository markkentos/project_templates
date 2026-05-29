# Руководство по паттернам проектирования в проекте «Anime Shelf»

В данном файле приведено краткое и наглядное описание всех **14 паттернов проектирования GoF**, реализованных в системе. Это руководство поможет вам быстро сориентироваться в архитектуре проекта и продемонстрировать преподавателю места внедрения каждого паттерна.

---

## 🏗️ Структурные паттерны (Structural Patterns)

### 1. Facade (Фасад)
*   **Где реализован**: [store/services/facade.py](/Users/dariagoryachko/mospolitech/shpp/project_templates/store/services/facade.py) (`StoreFacade`)
*   **Описание**: Объединяет подсистемы каталога, аналитики, команд, состояний и дерева категорий в единую точку входа. Django-представления из [store/views.py](/Users/dariagoryachko/mospolitech/shpp/project_templates/store/views.py) работают в основном через `StoreFacade`, не обращаясь напрямую к низкоуровневым сервисам.

### 2. Proxy (Заместитель)
*   **Где реализован**: [store/services/proxy.py](/Users/dariagoryachko/mospolitech/shpp/project_templates/store/services/proxy.py) (`ProductCatalogProxy`)
*   **Описание**: Оборачивает доступ к СУБД для получения каталога товаров. Фильтрует только активные товары и кэширует результаты выборок в памяти, снижая количество повторных SQL-запросов.

### 3. Adapter (Адаптер)
*   **Где реализован**: [store/services/adapter.py](/Users/dariagoryachko/mospolitech/shpp/project_templates/store/services/adapter.py) (`AnimeTrendAdapter`)
*   **Описание**: Адаптирует внешний несовместимый API трендов (`LegacyAnimeTrendClient`) под интерфейс нашего каталога, преобразуя данные на лету для вывода блока рекомендаций «Сейчас часто ищут».

### 4. Composite (Компоновщик)
*   **Где реализован**: [store/services/composite.py](/Users/dariagoryachko/mospolitech/shpp/project_templates/store/services/composite.py) (`CatalogComponent`, `CategoryNode`, `ProductLeaf`)
*   **Описание**: Позволяет представить структуру категорий каталога любой глубины и вложенных в них товаров в виде единого дерева. `CategoryNode` выступает контейнером, а `ProductLeaf` — листом.

### 5. Decorator (Декоратор)
*   **Где реализован**: [store/services/factories.py](/Users/dariagoryachko/mospolitech/shpp/project_templates/store/services/factories.py) (`ProductDataDecorator`, `LimitedEditionDecorator`, `GiftWrapDecorator`)
*   **Описание**: Динамически расширяет словарь параметров товара перед сохранением в БД. Используется при генерации демо-каталога для добавления свойств лимитированной серии и подарочной упаковки.

---

## ⚙️ Поведенческие паттерны (Behavioral Patterns)

### 6. Strategy (Стратегия)
*   **Где реализован**:
    *   [store/services/pricing.py](/Users/dariagoryachko/mospolitech/shpp/project_templates/store/services/pricing.py) (`PricingStrategy`, `RegularPricingStrategy`, `OtakuClubPricingStrategy`, `PromoPricingStrategy`)
    *   [store/services/shipping.py](/Users/dariagoryachko/mospolitech/shpp/project_templates/store/services/shipping.py) (`ShippingStrategy`, `PickupShippingStrategy`, `CourierShippingStrategy`, `ExpressShippingStrategy`)
*   **Описание**: Позволяет на лету переключать алгоритмы расчета цены и доставки в корзине и на checkout. Сейчас в проекте есть несколько стратегий скидки и несколько стратегий доставки, выбираемых пользователем через интерфейс.

### 7. Template Method (Шаблонный метод)
*   **Где реализован**:
    *   [store/services/processes.py](/Users/dariagoryachko/mospolitech/shpp/project_templates/store/services/processes.py) (`OrderProcessTemplate.execute`, `StandardOrderProcess`)
    *   [store/services/processes.py](/Users/dariagoryachko/mospolitech/shpp/project_templates/store/services/processes.py) (`ProductGenerationTemplate.generate`, `DemoCatalogGenerationTemplate`)
*   **Описание**: Фиксирует скелет алгоритма для оформления заказа и генерации демо-каталога. Например, checkout всегда идет по этапам проверки корзины, копирования позиций, пересчета сумм, списания остатков, закрытия корзины и публикации событий.

### 8. Iterator (Итератор)
*   **Где реализован**: [store/services/composite.py](/Users/dariagoryachko/mospolitech/shpp/project_templates/store/services/composite.py) (`CatalogIterator`)
*   **Описание**: Инкапсулирует обход сложного дерева категорий (Composite) в линейный и плоский список для его удобного рендеринга на веб-страницах.

### 9. Command & Undo (Команда и Отмена)
*   **Где реализован**: [store/services/commands.py](/Users/dariagoryachko/mospolitech/shpp/project_templates/store/services/commands.py) (`Command`, `AddToCartCommand`, `UpdateCartItemCommand`, `RemoveCartItemCommand`, `CheckoutCommand`, `AdvanceOrderStateCommand`, `CommandHistoryRegistry`)
*   **Описание**: Инкапсулирует изменяющие действия с корзиной и заказом в объекты-команды. `CommandHistoryRegistry` хранит историю команд по `session_key`, а после авторизации эта история переносится на новую сессию вместе с корзиной.

### 10. State (Состояние)
*   **Где реализован**: [store/services/states.py](/Users/dariagoryachko/mospolitech/shpp/project_templates/store/services/states.py) (`OrderState`, `CreatedState`, `PaidState`, `PackedState`, `ShippedState`, `DeliveredState`, `CancelledState`, `OrderStateMachine`)
*   **Описание**: Управляет жизненным циклом заказа. Заказ делегирует свое поведение объекту состояния. Каждый класс состояния жестко декларирует только разрешенные переходы (например, из `CREATED` в `PAID`), защищая логику от ошибок.

### 11. Observer (Наблюдатель)
*   **Где реализован**: [store/services/observers.py](/Users/dariagoryachko/mospolitech/shpp/project_templates/store/services/observers.py) (`Observer`, `EventBus`, `ProcessLogObserver`, `LowStockObserver`, `NotificationObserver`)
*   **Описание**: Реализует слабую связанность при возникновении бизнес-событий, таких как создание заказа или смена его статуса. События публикуются в `EventBus`, а наблюдатели автоматически пишут лог, проверяют низкий остаток и формируют уведомления.

---

## 🏭 Порождающие паттерны (Creational Patterns)

### 12. Singleton (СОдиночка)
*   **Где реализован**:
    *   [store/services/facade.py](/Users/dariagoryachko/mospolitech/shpp/project_templates/store/services/facade.py) (`StoreFacade`)
    *   [store/services/singletons.py](/Users/dariagoryachko/mospolitech/shpp/project_templates/store/services/singletons.py) (`StoreSettings`)
    *   [store/services/commands.py](/Users/dariagoryachko/mospolitech/shpp/project_templates/store/services/commands.py) (`CommandHistoryRegistry`)
    *   [store/services/observers.py](/Users/dariagoryachko/mospolitech/shpp/project_templates/store/services/observers.py) (`EventBus`)
    *   [store/services/pricing.py](/Users/dariagoryachko/mospolitech/shpp/project_templates/store/services/pricing.py) (`PricingStrategyRegistry`)
    *   [store/services/shipping.py](/Users/dariagoryachko/mospolitech/shpp/project_templates/store/services/shipping.py) (`ShippingStrategyRegistry`)
*   **Описание**: Гарантирует, что данные глобальные классы-сервисы существуют ровно в одном экземпляре на все время работы приложения.

### 13. Abstract Factory (Абстрактная фабрика)
*   **Где реализован**: [store/services/factories.py](/Users/dariagoryachko/mospolitech/shpp/project_templates/store/services/factories.py) (`AbstractMerchFactory`, `FigureFactory`, `ApparelFactory`, `PrintFactory`, `MangaFactory`, `AccessoryFactory`)
*   **Описание**: Предоставляет интерфейс для создания семейств взаимосвязанных объектов разных типов аниме-мерча без явного указания конкретного класса в коде генерации каталога.

### 14. Factory Method (Фабричный метод)
*   **Где реализован**: [store/services/factories.py](/Users/dariagoryachko/mospolitech/shpp/project_templates/store/services/factories.py) (`MerchFactoryProvider.get_factory`)
*   **Описание**: Делегирует выбор конкретной фабрики по строковому типу мерча (`figure`, `clothes`, `poster`, `manga`, `accessory`) и возвращает подходящую реализацию для генерации товара.
