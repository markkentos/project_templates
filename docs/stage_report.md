# Отчёт о соответствии проекта этапам ТЗ

В данном отчёте приведено детальное сопоставление реализованной кодовой базы проекта **«Anime Shelf»** требованиям 5 этапов учебного технического задания (с учетом новейших паттернов **Фабричный метод** и **Отмена команды (Undo)**).

---

## Этап 1: Проектирование и базовое приложение
*   **1). Создание приложения**  
    *Реализация:* Создан проект Django `anime_shop` (конфигурационная папка проекта) и отдельное модульное Django-приложение `store` (бизнес-логика).
*   **2). Создание БД**  
    *Реализация:* В проекте настроена СУБД SQLite. БД инициализирована, файл базы данных `db.sqlite3` находится в корне проекта.
*   **3). Запуск базового приложения**  
    *Реализация:* Базовое веб-приложение настроено и запускается через `python manage.py runserver`. Все системные миграции Django применены.
*   **4). Обновление схемы BPMN**  
    *Реализация:* Схемы двух ключевых бизнес-процессов (оформление заказа и импорт/генерация каталога) с отражением БД задокументированы в файле [docs/bpmn.md](file:///c:/Users/mark/Documents/university/2course/2sem/shpp/project_templates/docs/bpmn.md).
*   **5). Выделение сущностей и атрибутов**  
    *Реализация:* В файле [store/models.py](file:///c:/Users/mark/Documents/university/2course/2sem/shpp/project_templates/store/models.py) спроектированы Django-модели со строгими типами полей: `Category`, `Product`, `Customer`, `Cart`, `CartItem`, `Promotion`, `Order`, `OrderItem`, `Review`, `SalesPoint`, `ProcessLog`.
*   **6). Элемент с математической моделью**  
    *Реализация:* В файле [store/services/math_models.py](file:///c:/Users/mark/Documents/university/2course/2sem/shpp/project_templates/store/services/math_models.py) реализован класс `SalesTrendModel`. Он рассчитывает линейный тренд спроса по недельным точкам продаж методом наименьших квадратов ($y = ax + b$), сопоставляет прогноз с текущими остатками и строит оптимизированный прогноз продаж.
*   **7). Выделение паттернов: Стратегии, Состояния, Синглтоны**  
    *Реализация:*
    *   *Синглтоны:* `StoreSettings` в [singletons.py](file:///c:/Users/mark/Documents/university/2course/2sem/shpp/project_templates/store/services/singletons.py), реестры стратегий и шина событий.
    *   *Стратегии:* Расчет цен `PricingStrategy` в [pricing.py](file:///c:/Users/mark/Documents/university/2course/2sem/shpp/project_templates/store/services/pricing.py) и доставки `ShippingStrategy` в [shipping.py](file:///c:/Users/mark/Documents/university/2course/2sem/shpp/project_templates/store/services/shipping.py).
    *   *Состояния:* Жизненный цикл заказа `OrderStateMachine` и состояния `OrderState` в [states.py](file:///c:/Users/mark/Documents/university/2course/2sem/shpp/project_templates/store/services/states.py).

---

## Этап 2: Стратегии, Шаблонный метод, Фабрика и Декоратор
*   **1). Обновление схемы ERD**  
    *Реализация:* Полная ERD-диаграмма связей таблиц с атрибутами и типами связей задокументирована в [docs/erd.md](file:///c:/Users/mark/Documents/university/2course/2sem/shpp/project_templates/docs/erd.md).
*   **2). Создать БД**  
    *Реализация:* База данных полностью создана, применены все миграции приложения `store`.
*   **3). Заполнить БД (минимум 10 записей во ВСЕХ 11 таблицах)**  
    *Реализация:* Написана Django management-команда [store/management/commands/seed_store.py](file:///c:/Users/mark/Documents/university/2course/2sem/shpp/project_templates/store/management/commands/seed_store.py), которая при каждом запуске наполняет **абсолютно все 11 таблиц базы данных** (включая заказы, корзины, покупателей, отзывы и логи наблюдателя), гарантируя **минимум 10 уникальных записей в каждой таблице**. Все изображения переведены на **локальные SVG-векторы**, что гарантирует оффлайн-отображение.
*   **4). Шаблонный метод по BPMN (делегирование субклассирования)**  
    *Реализация:* В файле [store/services/processes.py](file:///c:/Users/mark/Documents/university/2course/2sem/shpp/project_templates/store/services/processes.py) реализован абстрактный класс `OrderProcessTemplate` с шаблонным методом `execute` (оформление заказа, списание остатков, оповещения). Делегирование субклассирования вынесено в абстрактный метод `prepare_comment`, реализуемый в `StandardOrderProcess` и `GiftOrderProcess`.
*   **5). Стратегии как части системы**  
    *Реализация:* Стратегии расчета стоимости корзины (`RegularPricingStrategy`, `OtakuClubPricingStrategy`, `PromoPricingStrategy`) и стоимости доставки (`PickupShippingStrategy`, `CourierShippingStrategy`, `ExpressShippingStrategy`) подключены и динамически выбираются пользователем в корзине `/cart/` и на странице оформления заказа.
*   **6). Реализация математической модели**  
    *Реализация:* Линейная регрессия спроса полностью интегрирована в карточку товара (/product/slug/) и на главную страницу для прогнозирования дефицита.
*   **7). Генерация через Абстрактную Фабрику и Декоратор**  
    *Реализация:* В файле [store/services/factories.py](file:///c:/Users/mark/Documents/university/2course/2sem/shpp/project_templates/store/services/factories.py) определен интерфейс `AbstractMerchFactory` и фабрики: `FigureFactory`, `ApparelFactory`, `PrintFactory`, `MangaFactory`, `AccessoryFactory`. Модификация сгенерированных товаров (например, лимитированная серия, добавление упаковки) выполняется через декораторы `LimitedEditionDecorator` и `GiftWrapDecorator`.

---

## Этап 3: Машина состояний, Адаптер, Наблюдатель, Команда
*   **1). Обновление диаграммы машины состояний**  
    *Реализация:* Диаграмма переходов состояний заказа (`created -> paid -> packed -> shipped -> delivered` и `cancelled`) задокументирована в [docs/state_machine.md](file:///c:/Users/mark/Documents/university/2course/2sem/shpp/project_templates/docs/state_machine.md).
*   **2). Подключение нового модуля через Адаптер**  
    *Реализация:* Внешний модуль трендов `LegacyAnimeTrendClient` возвращает несовместимый формат данных. В [store/services/adapter.py](file:///c:/Users/mark/Documents/university/2course/2sem/shpp/project_templates/store/services/adapter.py) реализован класс `AnimeTrendAdapter`, приводящий эти данные к стандартному интерфейсу рекомендаций магазина на главной странице.
*   **3). Реализовать Наблюдатель для отслеживания процесса**  
    *Реализация:* В файле [store/services/observers.py](file:///c:/Users/mark/Documents/university/2course/2sem/shpp/project_templates/store/services/observers.py) реализован синглтон-издатель `EventBus` и класс `Observer`. При изменении состояния заказа или создании нового заказа публикуются события `DomainEvent`. Зарегистрированные наблюдатели `ProcessLogObserver` (логирование в БД), `LowStockObserver` (предупреждение о низких остатках) и `NotificationObserver` (имитация отправки писем) получают оповещения и реагируют на них.
*   **4). Выполнение задач через интерфейс Команды (с отменой - Undo)**  
    *Реализация:* В файле [store/services/commands.py](file:///c:/Users/mark/Documents/university/2course/2sem/shpp/project_templates/store/services/commands.py) все действия пользователя инкапсулированы в классы команд, унаследованных от `Command` со встроенным методом отката `undo()`. Реализованы классы: `AddToCartCommand` (undo: списание добавленного), `UpdateCartItemCommand` (undo: откат к старой цене), `RemoveCartItemCommand` (undo: воссоздание позиции), `CheckoutCommand`, `AdvanceOrderStateCommand`. Реестр `CommandHistoryRegistry` обеспечивает ведение истории операций для отмены.
*   **5). Генерация элементов через Шаблонный метод**  
    *Реализация:* В [store/services/processes.py](file:///c:/Users/mark/Documents/university/2course/2sem/shpp/project_templates/store/services/processes.py) реализован шаблонный класс `ProductGenerationTemplate`, инкапсулирующий шаги парсинга, выбора фабрики, применения декораторов и записи товара в БД. Наследник `DemoCatalogGenerationTemplate` переопределяет один из шагов для добавления описания популярным товарам.

---

## Этап 4: UI, Фасад, Заместитель, Компоновщик, Итератор
*   **1). Финализация UI и доступ через Фасад**  
    *Реализация:* 
    *   Интерфейс оформлен в современном аниме-стиле с использованием адаптивной верстки (Vanilla CSS).
    *   Внедрена **интерактивная роль Менеджера** с полноценной панелью управления на главной странице (список и изменение статуса заказов, логов и сводная таблица критического дефицита).
    *   Внедрен **визуальный Stepper** для отслеживания состояний заказа и скрыто дублирование скидок при оформлении.
    *   В файле [store/services/facade.py](file:///c:/Users/mark/Documents/university/2course/2sem/shpp/project_templates/store/services/facade.py) созданы методы `StoreFacade` для доступа ко всей сложной логике. Django представления в [store/views.py](file:///c:/Users/mark/Documents/university/2course/2sem/shpp/project_templates/store/views.py) были полностью отрефакторены и обращаются к бизнес-логике исключительно через Фасад.
*   **2). Развертывание клиентской версии через Заместитель (Proxy)**  
    *Реализация:* В [store/services/proxy.py](file:///c:/Users/mark/Documents/university/2course/2sem/shpp/project_templates/store/services/proxy.py) реализован класс `ProductCatalogProxy`, который замещает оригинальный `ProductCatalogService` и кэширует результаты выборок товаров для ускорения работы каталога.
*   **3). Иерархия и перебор через Компоновщик и Итератор**  
    *Реализация:* В файле [store/services/composite.py](file:///c:/Users/mark/Documents/university/2course/2sem/shpp/project_templates/store/services/composite.py) иерархическое дерево категорий и товаров представлено классами `CategoryNode` (компоновщик) и `ProductLeaf` (лист), унаследованными от `CatalogComponent`. Для последовательного плоского обхода дерева по уровням реализован итератор `CatalogIterator`, который используется в UI `/tree/`.
*   **4). Обновление диаграммы классов до финального состояния**  
    *Реализация:* Полная UML-диаграмма классов с паттернами задокументирована в [docs/class_diagram.md](file:///c:/Users/mark/Documents/university/2course/2sem/shpp/project_templates/docs/class_diagram.md).

---

## Этап 5: Презентация и Защита
*   **1). PowerPoint-презентация (аналог)**  
    *Реализация:* Спроектирована стильная HTML-презентация-слайдер в папке [presentation/index.html](file:///c:/Users/mark/Documents/university/2course/2sem/shpp/project_templates/presentation/index.html).
*   **2). Подготовить рассказ о проекте и электронную доску**  
    *Реализация:* Подробный текст выступления для защиты написан в [presentation/defense_speech.md](file:///c:/Users/mark/Documents/university/2course/2sem/shpp/project_templates/presentation/defense_speech.md), а макет интерактивной доски спроектирован в [presentation/electronic_board.md](file:///c:/Users/mark/Documents/university/2course/2sem/shpp/project_templates/presentation/electronic_board.md).
*   **3). Use Case диаграмма в презентации**  
    *Реализация:* Полная диаграмма прецедентов использования построена на Mermaid в [docs/use_case.md](file:///c:/Users/mark/Documents/university/2course/2sem/shpp/project_templates/docs/use_case.md).
