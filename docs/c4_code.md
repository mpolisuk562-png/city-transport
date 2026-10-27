# C4 Code — діаграма класів

Рівень Code моделі C4 показує, з яких класів складається контейнер «REST API»:
доменні класи, абстрактний репозиторій і його реалізації, роутери та корінь композиції.

```mermaid
classDiagram
    direction LR

    %% ---------- Доменні класи (lab4/models.py) ----------
    class Route {
        +int id
        +str number
        +TransportType transport_type
        +str name
        +list~Vehicle~ vehicles
        +list~Stop~ stops
    }
    class Stop {
        +int id
        +str name
        +float latitude
        +float longitude
        +list~Route~ routes
    }
    class RouteStop {
        +int id
        +int route_id
        +int stop_id
        +int seq
    }
    class Driver {
        +int id
        +str full_name
        +str phone
        +str email
        +list~Vehicle~ vehicles
    }
    class Vehicle {
        +int id
        +str plate_number
        +str model
        +int year
        +int route_id
        +Optional~int~ driver_id
    }
    class TransportType {
        <<enumeration>>
        BUS
        TRAM
        TROLLEYBUS
    }

    Route "1" --> "0..*" Vehicle : route_id
    Driver "0..1" --> "0..*" Vehicle : driver_id
    Route "1" --> "0..*" RouteStop
    Stop "1" --> "0..*" RouteStop
    Route ..> TransportType

    %% ---------- Репозиторії (lab4/repositories) ----------
    class Repository~ModelT~ {
        <<abstract>>
        +get(item_id) ModelT
        +list(limit, offset, filters, order_by) Sequence~ModelT~
        +create(data) ModelT
        +update(item_id, data) ModelT
        +delete(item_id) None
    }
    class PostgresRepository~ModelT~ {
        -Session session
        -type~ModelT~ model
        -_commit() None
    }
    class InMemoryRepository~ModelT~ {
        -dict~int, ModelT~ _items
        -list _unique
        -_check_unique(obj, exclude_id) None
    }
    Repository <|-- PostgresRepository
    Repository <|-- InMemoryRepository

    class NotFoundError {
        <<exception>>
    }
    class ConflictError {
        <<exception>>
    }
    PostgresRepository ..> NotFoundError : raises
    PostgresRepository ..> ConflictError : IntegrityError →
    InMemoryRepository ..> NotFoundError : raises
    InMemoryRepository ..> ConflictError : raises

    %% ---------- Корінь композиції (lab4/dependencies.py) ----------
    class dependencies {
        <<composition root>>
        +STORAGES: dict~str, StorageFactory~
        +repository_for(model) Callable
        +RouteRepo, StopRepo, RouteStopRepo, DriverRepo, VehicleRepo
    }
    dependencies ..> PostgresRepository : creates
    dependencies ..> InMemoryRepository : creates

    %% ---------- Роутери (lab4/routers) ----------
    class routes_router {
        <<APIRouter /routes>>
        +list / get / create / update / delete
        +list_route_vehicles(route_id)
        +list_route_stops(route_id)
    }
    class vehicles_router {
        <<APIRouter /vehicles>>
        +list / get / create / update / delete
    }
    class stops_router {
        <<APIRouter /stops>>
        +list / get / create / update / delete
    }
    class route_stops_router {
        <<APIRouter /route-stops>>
        +list / get / create / update / delete
    }
    class drivers_router {
        <<APIRouter /drivers>>
        +list / get / create / update / delete
        +list_driver_vehicles(driver_id)
    }
    routes_router ..> Repository : Depends
    vehicles_router ..> Repository : Depends
    stops_router ..> Repository : Depends
    route_stops_router ..> Repository : Depends
    drivers_router ..> Repository : Depends
    routes_router ..> dependencies
    vehicles_router ..> dependencies
    stops_router ..> dependencies
    route_stops_router ..> dependencies
    drivers_router ..> dependencies

    %% ---------- Застосунок (lab4/restapi.py, lab4/handlers.py) ----------
    class FastAPIApp {
        <<restapi.app>>
        +include_router()
    }
    class handlers {
        +validation_handler() 422
        +not_found_handler() 404
        +conflict_handler() 409
    }
    FastAPIApp o-- routes_router
    FastAPIApp o-- vehicles_router
    FastAPIApp o-- stops_router
    FastAPIApp o-- route_stops_router
    FastAPIApp o-- drivers_router
    FastAPIApp ..> handlers
    handlers ..> NotFoundError
    handlers ..> ConflictError
```

## Як діаграма показує Open/Closed Principle

- Стрілки від роутерів ведуть лише до **абстрактного** `Repository<ModelT>`, а не до `PostgresRepository` чи `InMemoryRepository`.
- Конкретні класи знає тільки `dependencies` (корінь композиції). Нове сховище, наприклад `MongoRepository`, додається як ще один нащадок `Repository` і один рядок у `STORAGES`. Роутери, моделі та наявні репозиторії не змінюються.
- Новий ресурс додається як нова модель, нові схеми, новий модуль-роутер і один рядок у `ALL_ROUTERS`. Наявні класи також не редагуються.
- Репозиторії кидають доменні `NotFoundError` / `ConflictError`, а не `HTTPException`, тому шар збереження не залежить від FastAPI.
