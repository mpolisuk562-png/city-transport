# Демонстрація REST API

## Підготовка

```bash
docker compose up -d
uv run python -m lab4.init_db
uv run uvicorn lab4.restapi:app --reload
```

Swagger UI: http://127.0.0.1:8000/docs

Команди нижче запускаються з кореня проєкту. Тіла запитів лежать у `docs/requests/*.json` і передаються через `--data-binary @файл`. На Windows це важливо: Git Bash і PowerShell 5.1 передають кирилицю в аргументах командного рядка не в UTF-8, і сервер відповідає `400 There was an error parsing the body`. У PowerShell пишіть `curl.exe`, а не `curl`, бо `curl` там є аліасом `Invoke-WebRequest`.

Очікувані відповіді нижче наведено для щойно ініціалізованої БД із параметрами за замовчуванням (`uv run python -m lab4.init_db`: 25 водіїв, 40 машин, `--seed 42`, разом 167 записів). Водії та машини генеруються випадково, але той самий seed щоразу дає ті самі дані. З іншими `--drivers`, `--vehicles` чи `--seed` id, номери та імена в прикладах будуть іншими.

---

## 1. READ: список із пагінацією

```bash
curl -i "http://127.0.0.1:8000/routes?limit=3&offset=0"
```

```
HTTP/1.1 200 OK
[{"id":1,"number":"1","transport_type":"tram","name":"Головний вокзал — вул. Пекарська"},
 {"id":2,"number":"2","transport_type":"tram","name":"Вул. Шевченка — пл. Соборна"},
 {"id":3,"number":"6","transport_type":"tram","name":"Головний вокзал — вул. Липинського"}]
```

## 2. READ: запис за id

```bash
curl -i http://127.0.0.1:8000/routes/13
```

```
HTTP/1.1 200 OK
{"id":13,"number":"47","transport_type":"bus","name":"Аеропорт — Головний вокзал"}
```

## 3. Зв'язки: зупинки маршруту (N:M) і транспорт маршруту (1:N)

```bash
curl -i http://127.0.0.1:8000/routes/13/stops
```

```
HTTP/1.1 200 OK
[{"id":23,"name":"Аеропорт","latitude":49.8125,"longitude":23.956,"seq":1},
 {"id":11,"name":"Двірцева площа","latitude":49.8392,"longitude":23.9985,"seq":2},
 {"id":10,"name":"Головний залізничний вокзал","latitude":49.8394,"longitude":23.9944,"seq":3}]
```

```bash
curl -i http://127.0.0.1:8000/routes/13/vehicles
```

```
HTTP/1.1 200 OK
[{"id":13,"plate_number":"НС2536МХ","model":"Електрон А185","year":2024,"route_id":13,"driver_id":2},
 {"id":15,"plate_number":"ВС3044ВХ","model":"Електрон А185","year":2018,"route_id":13,"driver_id":22},
 {"id":25,"plate_number":"НС9189ВМ","model":"Електрон А185","year":2017,"route_id":13,"driver_id":23},
 {"id":37,"plate_number":"ВС4920ОО","model":"MAN Lion's City","year":2020,"route_id":13,"driver_id":14},
 {"id":39,"plate_number":"ВС4978ОІ","model":"Богдан А70132","year":2014,"route_id":13,"driver_id":19}]
```

Машини водія (зв'язок Driver 1:N Vehicle):

```bash
curl -i http://127.0.0.1:8000/drivers/2/vehicles
```

```
HTTP/1.1 200 OK
[{"id":4,"plate_number":"ВС0117ОЕ","model":"Electron T5L64","year":2015,"route_id":4,"driver_id":2},
 {"id":13,"plate_number":"НС2536МХ","model":"Електрон А185","year":2024,"route_id":13,"driver_id":2},
 {"id":23,"plate_number":"ВС4325ОР","model":"Tatra KT4","year":1985,"route_id":6,"driver_id":2},
 {"id":35,"plate_number":"ВС6311МХ","model":"MAN Lion's City","year":2023,"route_id":14,"driver_id":2}]
```

## 4. CREATE

`docs/requests/vehicle_create.json`:
```json
{"plate_number": "ВС7777АК", "model": "Електрон А185", "year": 2024, "route_id": 13, "driver_id": 5}
```

```bash
curl -i -X POST http://127.0.0.1:8000/vehicles -H "Content-Type: application/json" --data-binary @docs/requests/vehicle_create.json
```

```
HTTP/1.1 201 Created
{"id":41,"plate_number":"ВС7777АК","model":"Електрон А185","year":2024,"route_id":13,"driver_id":5}
```

```bash
curl -i http://127.0.0.1:8000/vehicles/41
```

```
HTTP/1.1 200 OK
{"id":41,"plate_number":"ВС7777АК","model":"Електрон А185","year":2024,"route_id":13,"driver_id":5}
```

## 5. UPDATE

PUT змінює лише передані поля. `null` дозволений тільки для `driver_id` і означає «відкріпити водія».

`docs/requests/vehicle_update.json`:
```json
{"route_id": 14, "driver_id": null}
```

```bash
curl -i -X PUT http://127.0.0.1:8000/vehicles/41 -H "Content-Type: application/json" --data-binary @docs/requests/vehicle_update.json
```

```
HTTP/1.1 200 OK
{"id":41,"plate_number":"ВС7777АК","model":"Електрон А185","year":2024,"route_id":14,"driver_id":null}
```

> На цьому кроці зручно перевірити в DBeaver, що зміни дійсно в БД (розділ 9).

## 6. DELETE

```bash
curl -i -X DELETE http://127.0.0.1:8000/vehicles/41
```

```
HTTP/1.1 204 No Content
```

```bash
curl -i http://127.0.0.1:8000/vehicles/41
```

```
HTTP/1.1 404 Not Found
{"detail":"Vehicle з id=41 не знайдено"}
```

## 7. Валідація regex: 422

`docs/requests/vehicle_invalid.json`:
```json
{"plate_number": "вс77АК", "model": "Електрон А185", "year": 1900, "route_id": 13}
```

```bash
curl -i -X POST http://127.0.0.1:8000/vehicles -H "Content-Type: application/json" --data-binary @docs/requests/vehicle_invalid.json
```

```
HTTP/1.1 422 Unprocessable Content
{"detail":"Некоректні вхідні дані","errors":[
  {"field":"plate_number","message":"Держномер має формат АА1234ВВ: 2 великі літери, 4 цифри, 2 великі літери","input":"вс77АК"},
  {"field":"year","message":"Значення має бути не менше 1950","input":1900}]}
```

`docs/requests/driver_invalid.json`:
```json
{"full_name": "Петренко Ігор Олексійович", "phone": "0671234567", "email": "ihor.lviv", "role": "admin"}
```

```bash
curl -i -X POST http://127.0.0.1:8000/drivers -H "Content-Type: application/json" --data-binary @docs/requests/driver_invalid.json
```

```
HTTP/1.1 422 Unprocessable Content
{"detail":"Некоректні вхідні дані","errors":[
  {"field":"phone","message":"Телефон має формат +380XXXXXXXXX (код країни і 9 цифр)","input":"0671234567"},
  {"field":"email","message":"Некоректний email, очікується формат name@example.com","input":"ihor.lviv"},
  {"field":"role","message":"Невідоме поле","input":"admin"}]}
```

```bash
curl -i "http://127.0.0.1:8000/routes?limit=1000"
```

```
HTTP/1.1 422 Unprocessable Content
{"detail":"Некоректні вхідні дані","errors":[{"field":"query.limit","message":"Значення має бути не більше 100","input":"1000"}]}
```

## 8. Порушення цілісності: 409

Дублікат держномера (`docs/requests/vehicle_duplicate.json`, номер `ВС4342ВМ` уже є в БД):

```bash
curl -i -X POST http://127.0.0.1:8000/vehicles -H "Content-Type: application/json" --data-binary @docs/requests/vehicle_duplicate.json
```

```
HTTP/1.1 409 Conflict
{"detail":"Конфлікт даних: Key (plate_number)=(ВС4342ВМ) already exists."}
```

Неіснуючий маршрут, тобто порушення FOREIGN KEY (`docs/requests/vehicle_bad_route.json`, `route_id: 999`):

```bash
curl -i -X POST http://127.0.0.1:8000/vehicles -H "Content-Type: application/json" --data-binary @docs/requests/vehicle_bad_route.json
```

```
HTTP/1.1 409 Conflict
{"detail":"Конфлікт даних: Key (route_id)=(999) is not present in table \"routes\"."}
```

Видалення маршруту, на якому ще працює транспорт (`ON DELETE RESTRICT`):

```bash
curl -i -X DELETE http://127.0.0.1:8000/routes/13
```

```
HTTP/1.1 409 Conflict
{"detail":"Конфлікт даних: Key (id)=(13) is referenced from table \"vehicles\"."}
```

---

## 9. Перевірка в DBeaver, що дані збереглися

Підключення: **PostgreSQL**, Host `localhost`, Port `5432`, Database `postgres`, User `postgres`, Password `postgres`.

Після кроку 5 (UPDATE) машина вже на маршруті 14 і без водія:

```sql
SELECT v.id, v.plate_number, v.model, v.year,
       r.number AS route_number, r.transport_type,
       d.full_name AS driver
FROM vehicles v
JOIN routes r ON r.id = v.route_id
LEFT JOIN drivers d ON d.id = v.driver_id
WHERE v.plate_number = 'ВС7777АК';
```

| id | plate_number | model | year | route_number | transport_type | driver |
|---|---|---|---|---|---|---|
| 41 | ВС7777АК | Електрон А185 | 2024 | 53 | bus | NULL |

Одразу після кроку 4 (CREATE), до оновлення, той самий запит покаже маршрут 47 і водія «Лисенко Ірина Миколаївна».

Після кроку 6 (DELETE) той самий запит повертає 0 рядків.

Зупинки маршруту в порядку проходження (зв'язок N:M):

```sql
SELECT r.number, r.transport_type, rs.seq, s.name
FROM routes r
JOIN route_stops rs ON rs.route_id = r.id
JOIN stops s ON s.id = rs.stop_id
WHERE r.number = '47' AND r.transport_type = 'bus'
ORDER BY rs.seq;
```

Кількість записів у кожній таблиці (разом 167 після `init_db` з параметрами за замовчуванням):

```sql
SELECT 'routes' AS tbl, count(*) FROM routes
UNION ALL SELECT 'stops', count(*) FROM stops
UNION ALL SELECT 'route_stops', count(*) FROM route_stops
UNION ALL SELECT 'drivers', count(*) FROM drivers
UNION ALL SELECT 'vehicles', count(*) FROM vehicles;
```
