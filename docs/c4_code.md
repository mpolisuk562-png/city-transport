# C4 Code — діаграма класів

Рівень Code моделі C4 показує, з яких класів складається контейнер «REST API»:
доменні класи, абстрактний репозиторій і його реалізації, роутери та функції,
що підставляють репозиторій у роутери.

```mermaid
classDiagram
    direction LR

    %% ---------- Доменні класи (lab4/models.py) ----------
    class Entity {
        +int id
    }
    class Route {
        +str number
        +str transport_type
        +str name
    }
    class Stop {
        +str name
        +float latitude
        +float longitude
    }
    class RouteStop {
        +int route_id
        +int stop_id
        +int seq
    }
    class Driver {
        +str full_name
        +str phone
        +str email
    }
    class Vehicle {
        +str plate_number
        +str model
        +int year
        +int route_id
        +Optional~int~ driver_id
    }
    Entity <|-- Route
    Entity <|-- Stop
    Entity <|-- RouteStop
    Entity <|-- Driver
    Entity <|-- Vehicle
    Route "1" --> "0..*" Vehicle : route_id
    Driver "0..1" --> "0..*" Vehicle : driver_id
    Route "1" --> "0..*" RouteStop : route_id
    Stop "1" --> "0..*" RouteStop : stop_id

    %% ---------- Репозиторії (lab4/repositories) ----------
    class Repository~ModelT~ {
        <<abstract>>
        +get(item_id) ModelT or None
        +list_all(filters) list~ModelT~
        +create(data) ModelT
        +update(obj, data) ModelT
        +delete(obj) None
    }
    class PostgresRepository~ModelT~ {
        -Session session
    }
    class InMemoryRepository~ModelT~ {
        -dict items
        -int next_id
    }
    Repository <|-- PostgresRepository
    Repository <|-- InMemoryRepository

    %% ---------- Вибір сховища (lab4/dependencies.py) ----------
    class dependencies {
        <<module>>
        +make_repository(model, session) Repository
        +get_route_repo() / get_vehicle_repo() / ...
    }
    dependencies ..> PostgresRepository : STORAGE=postgres
    dependencies ..> InMemoryRepository : STORAGE=memory

    %% ---------- Роутери (lab4/routers): routes, vehicles, stops, route-stops, drivers ----------
    class routers {
        <<APIRouter>>
        +list / get / create / update / delete
        +get_or_404(repo, item_id)
    }
    routers ..> Repository : Depends
    routers ..> dependencies

    %% ---------- Застосунок (lab4/restapi.py) ----------
    class FastAPIApp {
        <<restapi.app>>
        +include_router()
    }
    FastAPIApp o-- routers
```

## Як діаграма показує Open/Closed Principle

- Роутери залежать лише від **абстрактного** `Repository<ModelT>`, а не від `PostgresRepository` чи `InMemoryRepository`.
- Конкретне сховище обирає тільки `dependencies.make_repository()` за змінною `STORAGE`.
- Нове сховище (наприклад, `MongoRepository`) додається як ще один нащадок `Repository` і одна гілка в `make_repository()`. Роутери, моделі та наявні репозиторії не змінюються.
- Новий ресурс — це нова модель, схема, модуль-роутер і один рядок у `restapi.py`.
