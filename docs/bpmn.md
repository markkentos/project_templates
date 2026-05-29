# Схемы бизнес-процессов (BPMN)

В системе реализовано 2 основных бизнес-процесса (БП), спроектированных в соответствии с нотацией BPMN и полностью отражающих работу с базой данных:
1. **БП «Оформление заказа»** (интегрирован с паттерном *Шаблонный метод* и *Состояния*).
2. **БП «Импорт и генерация демо-каталога»** (интегрирован с паттернами *Шаблонный метод*, *Абстрактная Фабрика* и *Декоратор*).

---

## 1. БП «Оформление заказа»

### Описание процесса:
Процесс запускается, когда покупатель отправляет заполненную форму корзины. Система выполняет транзакционную проверку, сохраняет информацию о покупателе, создает заказ в статусе `CREATED`, резервирует остатки товара на складе, применяет стратегии расчета цен и доставки, после чего отправляет уведомления через шину событий.

### BPMN-схема процесса на Mermaid:

```mermaid
%%{init: {'theme': 'neutral'}}%%
graph TD
    %% Пулы/Дорожки
    subgraph Buyer ["Покупатель (Client Lane)"]
        Start1([Начало: Клик 'Оформить заказ']) --> SendForm[Отправить форму с данными]
        ShowSuccess[Получить страницу заказа #ID] --> End1([Конец: Заказ оформлен])
    end

    subgraph System ["Система магазина (System Lane)"]
        SendForm --> ValidateCart{Корзина пуста?}
        ValidateCart -- Да --> ThrowError[Показать ошибку] --> SendForm
        ValidateCart -- Нет --> CheckStock{Товара хватает?}
        
        CheckStock -- Нет --> ThrowError
        CheckStock -- Да --> GetOrCreateCustomer[Найти/Создать Customer]
        GetOrCreateCustomer --> CreateOrder[Создать Order статус: CREATED]
        CreateOrder --> CopyItems[Скопировать CartItem в OrderItem]
        CopyItems --> CalculatePricing[Применить PricingStrategy]
        CalculatePricing --> CalculateShipping[Применить ShippingStrategy]
        CalculateShipping --> SubStock[Списать остатки Product.stock]
        SubStock --> CloseCart[Закрыть Cart статус: checked_out]
        CloseCart --> PublishEvent[Опубликовать DomainEvent: order.created]
        PublishEvent --> Redirect[Перенаправить на детали заказа]
        Redirect --> ShowSuccess
    end

    subgraph DB ["База данных (Database Lane)"]
        GetOrCreateCustomer -.-> DB_Customer[(Таблица Customer)]
        CreateOrder -.-> DB_Order[(Таблица Order)]
        CopyItems -.-> DB_OrderItem[(Таблица OrderItem)]
        SubStock -.-> DB_Product[(Таблица Product)]
        CloseCart -.-> DB_Cart[(Таблица Cart)]
        PublishEvent -.-> DB_ProcessLog[(Таблица ProcessLog)]
    end

    %% Стилизация
    classDef buyer fill:#fdf6e3,stroke:#b58900,stroke-width:2px;
    classDef system fill:#eee8d5,stroke:#268bd2,stroke-width:2px;
    classDef database fill:#f6f4ef,stroke:#586e75,stroke-width:2px;
    class SendForm,ShowSuccess,Start1,End1 buyer;
    class ValidateCart,CheckStock,GetOrCreateCustomer,CreateOrder,CopyItems,CalculatePricing,CalculateShipping,SubStock,CloseCart,PublishEvent,Redirect system;
    class DB_Customer,DB_Order,DB_OrderItem,DB_Product,DB_Cart,DB_ProcessLog database;
```

---

## 2. БП «Пополнение каталога и аналитика спроса»

### Описание процесса:
Процесс состоит из двух связанных частей. Сначала администратор подготавливает демонстрационный каталог через консольную команду `python manage.py seed_store`: система очищает старые записи, пересобирает категории, товары, промоакции и точки продаж. Затем менеджер входит в веб-интерфейс, открывает вкладку прогноза спроса, выбирает товар и получает расчет от `SalesTrendModel` на основе `SalesPoint` и текущего остатка `Product.stock`.

### BPMN-схема процесса на Mermaid:

```mermaid
%%{init: {'theme': 'neutral'}}%%
graph TD
    subgraph Admin ["Администратор / Менеджер"]
        Start2([Старт]) --> RunSeed[Администратор запускает seed_store]
        ManagerLogin[Менеджер входит в систему] --> OpenForecast[Открыть /manager?tab=forecast]
        ShowForecast[Получить прогноз и рекомендацию] --> End2([Конец])
    end

    subgraph System ["Система генератора (System Lane)"]
        RunSeed --> Cleanup[Очистить старые демо-данные и сбросить кэш ProductCatalogProxy]
        Cleanup --> CreateCategories[Создать Category и Promotion]
        CreateCategories --> GenerateCatalog[Сгенерировать Product через Template Method + Abstract Factory + Decorator]
        GenerateCatalog --> CreateSales[Создать недельные точки продаж SalesPoint]
        CreateSales --> SeedUsers[Создать demo Customer и manager-аккаунты]
        SeedUsers --> SeedDone[Вывести отчет: каталог и аналитические данные готовы]
        SeedDone --> ManagerLogin
        OpenForecast --> CheckRole{Пользователь is_staff?}
        CheckRole -- Нет --> Deny[Запретить доступ]
        CheckRole -- Да --> SelectProduct[Показать список товаров и выбранный Product]
        SelectProduct --> LoadTrendData[Загрузить Product.sales_points и Product.stock]
        LoadTrendData --> CalculateTrend[Рассчитать SalesTrendModel]
        CalculateTrend --> ShowForecast
    end

    subgraph DB ["База данных (Database Lane)"]
        CreateCategories -.-> DB_Category[(Category)]
        CreateCategories -.-> DB_Promotion[(Promotion)]
        GenerateCatalog -.-> DB_Product[(Product)]
        CreateSales -.-> DB_SalesPoint[(SalesPoint)]
        SeedUsers -.-> DB_User[(auth.User)]
        SeedUsers -.-> DB_Customer[(Customer)]
        LoadTrendData -.-> DB_Product
        LoadTrendData -.-> DB_SalesPoint
    end

    %% Стилизация
    classDef buyer fill:#fdf6e3,stroke:#b58900,stroke-width:2px;
    classDef system fill:#eee8d5,stroke:#268bd2,stroke-width:2px;
    classDef database fill:#f6f4ef,stroke:#586e75,stroke-width:2px;
    class Start2,RunSeed,ManagerLogin,OpenForecast,ShowForecast,End2 buyer;
    class Cleanup,CreateCategories,GenerateCatalog,CreateSales,SeedUsers,SeedDone,CheckRole,Deny,SelectProduct,LoadTrendData,CalculateTrend system;
    class DB_Category,DB_Promotion,DB_Product,DB_SalesPoint,DB_User,DB_Customer database;
```
