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

## 2. БП «Импорт и генерация демо-каталога»

### Описание процесса:
Процесс запускается администратором через консольную команду `python manage.py seed_store`. Он считывает массив демо-данных, последовательно определяет фабрику для каждой категории мерча, при необходимости декорирует данные (лимитированная серия, подарочная упаковка), создает или обновляет записи в БД, а также рассчитывает историю продаж для аналитической математической модели.

### BPMN-схема процесса на Mermaid:

```mermaid
%%{init: {'theme': 'neutral'}}%%
graph TD
    subgraph Admin ["Администратор (Admin Lane)"]
        Start2([Начало: Запуск команды seed_store]) --> CheckFinish([Конец: Демо-каталог готов])
    end

    subgraph System ["Система генератора (System Lane)"]
        Start2 --> CleanCache[Сбросить кэш ProductCatalogProxy]
        CleanCache --> LoadCategories[Создать структуру Category]
        LoadCategories --> LoopProducts[Для каждого товара в списке PRODUCTS]
        
        LoopProducts --> SelectFactory[Выбрать AbstractMerchFactory]
        SelectFactory --> CreatePayload[Сгенерировать базовые атрибуты]
        CreatePayload --> IsLimited{Лимитированная серия?}
        IsLimited -- Да --> DecorateLimited[Применить LimitedEditionDecorator: наценка +18%] --> IsGift
        IsLimited -- Нет --> IsGift{Подарочная упаковка?}
        
        IsGift -- Да --> DecorateGift[Применить GiftWrapDecorator: +250 руб.] --> PersistProduct
        IsGift -- Нет --> PersistProduct[Сохранить Product в БД]
        
        PersistProduct --> GenerateSales[Сгенерировать недельные продажи SalesPoint]
        GenerateSales --> LoopProducts
        LoopProducts -- Все обработаны --> PrintSuccess[Вывести отчет в консоль]
        PrintSuccess --> CheckFinish
    end

    subgraph DB ["База данных (Database Lane)"]
        LoadCategories -.-> DB_Category[(Таблица Category)]
        PersistProduct -.-> DB_Product2[(Таблица Product)]
        GenerateSales -.-> DB_SalesPoint[(Таблица SalesPoint)]
    end

    %% Стилизация
    classDef buyer fill:#fdf6e3,stroke:#b58900,stroke-width:2px;
    classDef system fill:#eee8d5,stroke:#268bd2,stroke-width:2px;
    classDef database fill:#f6f4ef,stroke:#586e75,stroke-width:2px;
    class Start2,CheckFinish buyer;
    class CleanCache,LoadCategories,LoopProducts,SelectFactory,CreatePayload,IsLimited,DecorateLimited,IsGift,DecorateGift,PersistProduct,GenerateSales,PrintSuccess system;
    class DB_Category,DB_Product2,DB_SalesPoint database;
```
