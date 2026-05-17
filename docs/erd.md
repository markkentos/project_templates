# ERD

```mermaid
erDiagram
    CATEGORY ||--o{ CATEGORY : parent
    CATEGORY ||--o{ PRODUCT : contains
    PRODUCT ||--o{ CART_ITEM : added
    CART ||--o{ CART_ITEM : includes
    CUSTOMER ||--o{ ORDER : places
    ORDER ||--o{ ORDER_ITEM : includes
    PRODUCT ||--o{ ORDER_ITEM : sold_as
    PRODUCT ||--o{ REVIEW : reviewed
    PRODUCT ||--o{ SALES_POINT : measured
    ORDER ||--o{ PROCESS_LOG : logs

    CATEGORY {
        int id
        string name
        string slug
        text description
        int parent_id
    }

    PRODUCT {
        int id
        int category_id
        string name
        string slug
        string anime_title
        string merch_type
        decimal price
        int stock
        decimal rating
        int popularity_score
        int sales_count
        string image_url
        bool is_active
    }

    CUSTOMER {
        int id
        string name
        string email
        string phone
        string city
    }

    CART {
        int id
        string session_key
        string status
    }

    CART_ITEM {
        int id
        int cart_id
        int product_id
        int quantity
    }

    ORDER {
        int id
        int customer_id
        string status
        string delivery_method
        string pricing_strategy
        decimal subtotal
        decimal discount
        decimal shipping_price
        decimal total
        text comment
    }

    ORDER_ITEM {
        int id
        int order_id
        int product_id
        string product_name
        decimal unit_price
        int quantity
    }

    PROMOTION {
        int id
        string name
        string code
        int discount_percent
        bool is_active
    }

    REVIEW {
        int id
        int product_id
        string customer_name
        int rating
        text text
    }

    SALES_POINT {
        int id
        int product_id
        int week_number
        int units_sold
    }

    PROCESS_LOG {
        int id
        int order_id
        string event_type
        string level
        text message
    }
```
