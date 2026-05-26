# Руководство по паттернам проектирования в проекте «Anime Shelf»

В данном файле приведено краткое и наглядное описание всех **14 паттернов проектирования GoF**, реализованных в системе. Это руководство поможет вам быстро сориентироваться в архитектуре проекта и продемонстрировать преподавателю места внедрения каждого паттерна.

---

## 🏗️ Структурные паттерны (Structural Patterns)

### 1. Facade (Фасад)
*   **Где реализован**: [store/services/facade.py](file:///c:/Users/mark/Documents/university/2course/2sem/shpp/project_templates/store/services/facade.py) (`StoreFacade`)
*   **Описание**: Объединяет подсистемы кэширования (Proxy), интеграций (Adapter), команд (Command), дерева (Composite) и бизнес-логики. Django-представления в [views.py](file:///c:/Users/mark/Documents/university/2course/2sem/shpp/project_templates/store/views.py) не знают о деталях реализации и обращаются исключительно к `StoreFacade`.

### 2. Proxy (Заместитель)
*   **Где реализован**: [store/services/proxy.py](file:///c:/Users/mark/Documents/university/2course/2sem/shpp/project_templates/store/services/proxy.py) (`ProductCatalogProxy`)
*   **Описание**: Оборачивает доступ к СУБД для получения каталога товаров. Фильтрует только активные товары и кэширует результаты выборок в памяти, снижая количество повторных SQL-запросов.

### 3. Adapter (Адаптер)
*   **Где реализован**: [store/services/adapter.py](file:///c:/Users/mark/Documents/university/2course/2sem/shpp/project_templates/store/services/adapter.py) (`AnimeTrendAdapter`)
*   **Описание**: Адаптирует внешний несовместимый API трендов (`LegacyAnimeTrendClient`) под интерфейс нашего каталога, преобразуя данные на лету для вывода блока рекомендаций «Сейчас часто ищут».

### 4. Composite (Компоновщик)
*   **Где реализован**: [store/services/composite.py](file:///c:/Users/mark/Documents/university/2course/2sem/shpp/project_templates/store/services/composite.py) (`CatalogComponent`, `CategoryNode`, `ProductLeaf`)
*   **Описание**: Позволяет представить структуру категорий каталога любой глубины и вложенных в них товаров в виде единого дерева. `CategoryNode` выступает контейнером, а `ProductLeaf` — листом.

### 5. Decorator (Декоратор)
*   **Где реализован**: [store/services/factories.py](file:///c:/Users/mark/Documents/university/2course/2sem/shpp/project_templates/store/services/factories.py) (`ProductDataDecorator`, `LimitedEditionDecorator`, `GiftWrapDecorator`)
*   **Описание**: Динамически и многослойно расширяет словарь параметров товара перед сохранением его в базу данных (например, добавляет пометки подарочной упаковки или ограниченного тиража).

---

## ⚙️ Поведенческие паттерны (Behavioral Patterns)

### 6. Strategy (Стратегия)
*   **Где реализован**:
    *   [store/services/pricing.py](file:///c:/Users/mark/Documents/university/2course/2sem/shpp/project_templates/store/services/pricing.py) (`PricingStrategy` и его наследники `RegularPricingStrategy`, `OtakuClubPricingStrategy`)
    *   [store/services/shipping.py](file:///c:/Users/mark/Documents/university/2course/2sem/shpp/project_templates/store/services/shipping.py) (`ShippingStrategy` и его наследники `PickupShippingStrategy`, `CourierShippingStrategy`)
*   **Описание**: Позволяет на лету переключать алгоритмы расчета стоимости корзины (обычная цена, скидки клуба отаку) и доставки (самовывоз, курьерская доставка) в зависимости от выбора пользователя.

### 7. Template Method (Шаблонный метод)
*   **Где реализован**:
    *   [store/services/processes.py](file:///c:/Users/mark/Documents/university/2course/2sem/shpp/project_templates/store/services/processes.py) (`OrderProcessTemplate.execute`, подклассы `StandardOrderProcess`, `GiftOrderProcess`)
    *   [store/services/processes.py](file:///c:/Users/mark/Documents/university/2course/2sem/shpp/project_templates/store/services/processes.py) (`ProductGenerationTemplate.generate`, подкласс `DemoCatalogGenerationTemplate`)
*   **Описание**: Фиксирует неизменный скелет алгоритма (например, создание заказа: проверка наличия -> списание со склада -> закрытие корзины), делегируя варьируемые шаги (форматирование комментария) подклассам.

### 8. Iterator (Итератор)
*   **Где реализован**: [store/services/composite.py](file:///c:/Users/mark/Documents/university/2course/2sem/shpp/project_templates/store/services/composite.py) (`CatalogIterator`)
*   **Описание**: Инкапсулирует обход сложного дерева категорий (Composite) в линейный и плоский список для его удобного рендеринга на веб-страницах.

### 9. Command & Undo (Команда и Отмена)
*   **Где реализован**: [store/services/commands.py](file:///c:/Users/mark/Documents/university/2course/2sem/shpp/project_templates/store/services/commands.py) (`Command`, `AddToCartCommand`, `UpdateCartItemCommand`, `RemoveCartItemCommand`, `CommandHistoryRegistry`)
*   **Описание**: Инкапсулирует все мутирующие операции с корзиной и заказами в объекты команд. Благодаря сохранению состояния «до» в стеке сессионного реестра `CommandHistoryRegistry`, пользователь может отменять свои действия по кнопке «Отменить последнее действие».

### 10. State (Состояние)
*   **Где реализован**: [store/services/states.py](file:///c:/Users/mark/Documents/university/2course/2sem/shpp/project_templates/store/services/states.py) (`OrderState`, подклассы `CreatedState`, `PaidState` и др., `OrderStateMachine`)
*   **Описание**: Управляет жизненным циклом заказа. Заказ делегирует свое поведение объекту состояния. Каждый класс состояния жестко декларирует только разрешенные переходы (например, из `CREATED` в `PAID`), защищая логику от ошибок.

### 11. Observer (Наблюдатель)
*   **Где реализован**: [store/services/observer.py](file:///c:/Users/mark/Documents/university/2course/2sem/shpp/project_templates/store/services/observer.py) (`Observer`, `EventBus`, `ProcessLogObserver`, `LowStockObserver`, `NotificationObserver`)
*   **Описание**: Реализует слабую связанность при возникновении бизнес-событий (создание заказа, смена статуса). Событие публикуется в шину `EventBus`, после чего наблюдатели автоматически записывают логи в БД, генерируют уведомления и отслеживают дефицит.

---

## 🏭 Порождающие паттерны (Creational Patterns)

### 12. Singleton (Синглтон)
*   **Где реализован**:
    *   [store/services/facade.py](file:///c:/Users/mark/Documents/university/2course/2sem/shpp/project_templates/store/services/facade.py) (`StoreFacade`)
    *   [store/services/settings.py](file:///c:/Users/mark/Documents/university/2course/2sem/shpp/project_templates/store/services/settings.py) (`StoreSettings`)
    *   [store/services/commands.py](file:///c:/Users/mark/Documents/university/2course/2sem/shpp/project_templates/store/services/commands.py) (`CommandHistoryRegistry`)
    *   [store/services/observer.py](file:///c:/Users/mark/Documents/university/2course/2sem/shpp/project_templates/store/services/observer.py) (`EventBus`)
*   **Описание**: Гарантирует, что данные глобальные классы-сервисы существуют ровно в одном экземпляре на все время работы приложения.

### 13. Abstract Factory (Абстрактная фабрика)
*   **Где реализован**: [store/services/factories.py](file:///c:/Users/mark/Documents/university/2course/2sem/shpp/project_templates/store/services/factories.py) (`AbstractMerchFactory` и его подклассы `FigureFactory`, `ApparelFactory`, `AccessoryFactory`)
*   **Описание**: Предоставляет интерфейс для создания семейств взаимосвязанных объектов (различных типов аниме-мерча) без указания их конкретных классов при генерации демо-каталога.

### 14. Factory Method (Фабричный метод)
*   **Где реализован**: [store/services/factories.py](file:///c:/Users/mark/Documents/university/2course/2sem/shpp/project_templates/store/services/factories.py) (`MerchFactoryProvider.get_factory`)
*   **Описание**: Определяет интерфейс для создания объектов (фабрик конкретных видов мерча), делегируя выбор нужного класса в зависимости от строки типа мерча.
