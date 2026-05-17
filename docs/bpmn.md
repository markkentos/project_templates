# BPMN

Диаграммы даны в Mermaid-формате, чтобы их можно было открыть в редакторе Markdown с поддержкой Mermaid.

## Бизнес-процесс 1: покупка товара

```mermaid
flowchart LR
    subgraph Customer[Покупатель]
        A([Старт]) --> B[Открыть каталог]
        B --> C[Выбрать товар]
        C --> D[Добавить в корзину]
        D --> E[Выбрать скидку и доставку]
        E --> F[Заполнить контакты]
    end

    subgraph Django[Веб-приложение Django]
        F --> G{Корзина валидна?}
        G -- нет --> H[Показать ошибку]
        G -- да --> I[OrderProcessTemplate]
        I --> J[Создать покупателя]
        J --> K[Создать заказ]
        K --> L[Скопировать позиции]
        L --> M[Применить Strategy цены]
        M --> N[Применить Strategy доставки]
        N --> O[Зарезервировать склад]
        O --> P[Опубликовать событие]
    end

    subgraph Database[База данных]
        DB1[(Customer)]
        DB2[(Cart, CartItem)]
        DB3[(Order, OrderItem)]
        DB4[(Product)]
        DB5[(ProcessLog)]
    end

    J --> DB1
    G --> DB2
    K --> DB3
    L --> DB3
    O --> DB4
    P --> DB5
    P --> Q([Заказ создан])
```

## Бизнес-процесс 2: пополнение каталога и аналитика спроса

```mermaid
flowchart LR
    subgraph Manager[Менеджер магазина]
        A([Старт]) --> B[Запустить seed_store]
        B --> C[Подготовить набор товаров]
    end

    subgraph App[Система]
        C --> D[ProductGenerationTemplate]
        D --> E[Abstract Factory выбирает тип товара]
        E --> F[Decorator добавляет limited/gift свойства]
        F --> G[Сохранить товары и категории]
        G --> H[Создать SalesPoint]
        H --> I[SalesTrendModel]
        I --> J[Показать прогноз спроса]
    end

    subgraph Database[База данных]
        DB1[(Category)]
        DB2[(Product)]
        DB3[(Promotion)]
        DB4[(SalesPoint)]
    end

    G --> DB1
    G --> DB2
    G --> DB3
    H --> DB4
    J --> K([Каталог готов])
```
