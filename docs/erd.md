# ERD — модель бази даних «Міський транспорт»

```mermaid
erDiagram
    ROUTES ||--o{ VEHICLES : "обслуговується (1:N)"
    DRIVERS |o--o{ VEHICLES : "закріплений за (1:N)"
    ROUTES ||--o{ ROUTE_STOPS : "містить"
    STOPS ||--o{ ROUTE_STOPS : "входить у"

    ROUTES {
        int id PK
        varchar number UK "UNIQUE (number, transport_type)"
        transport_type transport_type UK "bus | tram | trolleybus"
        varchar name
    }

    STOPS {
        int id PK
        varchar name
        float latitude "від -90 до 90"
        float longitude "від -180 до 180"
    }

    ROUTE_STOPS {
        int id PK
        int route_id FK "routes.id, ON DELETE CASCADE"
        int stop_id FK "stops.id, ON DELETE RESTRICT"
        int seq "порядковий номер, UNIQUE (route_id, seq)"
    }

    DRIVERS {
        int id PK
        varchar full_name
        varchar phone UK "+380XXXXXXXXX"
        varchar email UK
    }

    VEHICLES {
        int id PK
        varchar plate_number UK "АА1234ВВ"
        varchar model
        int year
        int route_id FK "routes.id, ON DELETE RESTRICT"
        int driver_id FK "drivers.id, nullable, ON DELETE SET NULL"
    }
```

## Зв'язки

| Зв'язок | Тип | Реалізація |
|---|---|---|
| Route → Vehicle | 1:N (з боку Vehicle — N:1) | `vehicles.route_id` → `routes.id` |
| Driver → Vehicle | 1:N, необов'язковий | `vehicles.driver_id` → `drivers.id` (NULL = водія не закріплено) |
| Route ↔ Stop | N:M | асоціативна таблиця `route_stops` з порядковим номером `seq` |

## Правила цілісності

- **UNIQUE**: держномер, телефон і email водія; пара (номер, тип) маршруту, бо номер «1» може мати і трамвай, і автобус; пари (маршрут, зупинка) і (маршрут, seq) у `route_stops`.
- **ON DELETE RESTRICT**: не можна видалити маршрут, за яким закріплено транспорт, і зупинку, що входить у маршрут. API відповідає `409 Conflict`.
- **ON DELETE CASCADE**: разом із маршрутом видаляється його список зупинок.
- **ON DELETE SET NULL**: якщо водія видалили, машина лишається без закріпленого водія.
