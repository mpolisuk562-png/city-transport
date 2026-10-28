# Демонстрація REST API

## Підготовка

```bash
docker compose up -d
uv run python -m lab4.init_db
uv run uvicorn lab4.restapi:app --reload
```

Swagger UI: http://127.0.0.1:8000/docs

Команди нижче запускаються з кореня проєкту. Тіла запитів лежать у `docs/requests/*.json` і передаються через `--data-binary @файл`. На Windows це важливо: Git Bash і PowerShell 5.1 передають кирилицю в аргументах командного рядка не в UTF-8. У PowerShell пишіть `curl.exe`, а не `curl`.

Відповіді нижче наведено для щойно ініціалізованої БД (`init_db`: 14 маршрутів, 28 зупинок, 60 зв'язків маршрут–зупинка, 20 водіїв, 35 машин). Водії та машини генеруються випадково, але з фіксованим зерном, тож після кожного `init_db` дані ті самі. Порядок полів у JSON може відрізнятися від наведеного, на зміст це не впливає.

---

## 1. READ: список

```bash
curl -i http://127.0.0.1:8000/routes
```

```
HTTP/1.1 200 OK
[{"transport_type":"tram","name":"Головний вокзал — вул. Пекарська","id":1,"number":"1"},
 {"transport_type":"tram","name":"Вул. Шевченка — пл. Соборна","id":2,"number":"2"},
 ...]
```

## 2. READ: запис за id

```bash
curl -i http://127.0.0.1:8000/routes/13
```

```
HTTP/1.1 200 OK
{"transport_type":"bus","name":"Аеропорт — Головний вокзал","id":13,"number":"47"}
```

## 3. Зв'язки: зупинки маршруту (N:M) і транспорт маршруту (1:N)

```bash
curl -i http://127.0.0.1:8000/routes/13/stops
```

```
HTTP/1.1 200 OK
[{"name":"Аеропорт","latitude":49.8125,"id":23,"longitude":23.956},
 {"name":"Двірцева площа","latitude":49.8392,"id":11,"longitude":23.9985},
 {"name":"Головний залізничний вокзал","latitude":49.8394,"id":10,"longitude":23.9944}]
```

```bash
curl -i http://127.0.0.1:8000/routes/13/vehicles
```

```
HTTP/1.1 200 OK
[{"year":2018,"id":13,"driver_id":19,"plate_number":"ВС6065ІА","model":"MAN Lion's City","route_id":13},
 {"year":2023,"id":28,"driver_id":18,"plate_number":"ВС5313КН","model":"MAN Lion's City","route_id":13}]
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
{"year":2024,"id":36,"driver_id":5,"plate_number":"ВС7777АК","model":"Електрон А185","route_id":13}
```

```bash
curl -i http://127.0.0.1:8000/vehicles/36
```

```
HTTP/1.1 200 OK
{"year":2024,"id":36,"driver_id":5,"plate_number":"ВС7777АК","model":"Електрон А185","route_id":13}
```

## 5. UPDATE

PUT передає запис повністю, як і POST. Тут машину переводять на маршрут 14 і відкріплюють водія.

`docs/requests/vehicle_update.json`:
```json
{"plate_number": "ВС7777АК", "model": "Електрон А185", "year": 2024, "route_id": 14, "driver_id": null}
```

```bash
curl -i -X PUT http://127.0.0.1:8000/vehicles/36 -H "Content-Type: application/json" --data-binary @docs/requests/vehicle_update.json
```

```
HTTP/1.1 200 OK
{"year":2024,"id":36,"driver_id":null,"plate_number":"ВС7777АК","model":"Електрон А185","route_id":14}
```

> На цьому кроці зручно перевірити в DBeaver, що зміни дійсно в БД (розділ 8).

## 6. DELETE

```bash
curl -i -X DELETE http://127.0.0.1:8000/vehicles/36
```

```
HTTP/1.1 204 No Content
```

```bash
curl -i http://127.0.0.1:8000/vehicles/36
```

```
HTTP/1.1 404 Not Found
{"detail":"Запис з id=36 не знайдено"}
```

## 7. Валідація regex: 422

`docs/requests/vehicle_invalid.json`: держномер малими літерами і з двома цифрами, рік 1900:
```json
{"plate_number": "вс77АК", "model": "Електрон А185", "year": 1900, "route_id": 13}
```

```bash
curl -i -X POST http://127.0.0.1:8000/vehicles -H "Content-Type: application/json" --data-binary @docs/requests/vehicle_invalid.json
```

```
HTTP/1.1 422 Unprocessable Content
{"detail":[
  {"type":"string_pattern_mismatch","loc":["body","plate_number"],"msg":"String should match pattern '^[A-ZА-ЯІЇЄ]{2}\\d{4}[A-ZА-ЯІЇЄ]{2}$'","input":"вс77АК",...},
  {"type":"greater_than_equal","loc":["body","year"],"msg":"Input should be greater than or equal to 1950","input":1900,...}]}
```

`docs/requests/driver_invalid.json`: телефон без `+380` і email без `@`:
```json
{"full_name": "Петренко Ігор Олексійович", "phone": "0671234567", "email": "ihor.lviv"}
```

```bash
curl -i -X POST http://127.0.0.1:8000/drivers -H "Content-Type: application/json" --data-binary @docs/requests/driver_invalid.json
```

```
HTTP/1.1 422 Unprocessable Content
{"detail":[
  {"type":"string_pattern_mismatch","loc":["body","phone"],"msg":"String should match pattern '^\\+380\\d{9}$'","input":"0671234567",...},
  {"type":"string_pattern_mismatch","loc":["body","email"],"msg":"String should match pattern '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$'","input":"ihor.lviv",...}]}
```

---

## 8. Перевірка в DBeaver, що дані збереглися

Підключення: **PostgreSQL**, Host `localhost`, Port `5432`, Database `postgres`, User `postgres`, Password `postgres`.

```sql
SELECT v.id, v.plate_number, v.model, v.year,
       r.number AS route_number, r.transport_type,
       d.full_name AS driver
FROM vehicles v
JOIN routes r ON r.id = v.route_id
LEFT JOIN drivers d ON d.id = v.driver_id
WHERE v.plate_number = 'ВС7777АК';
```

| Коли виконати | Результат |
|---|---|
| після кроку 4 (CREATE) | id 36, маршрут 47, водій «Коваленко Василь Ігорович» |
| після кроку 5 (UPDATE) | id 36, маршрут 53, водій NULL |
| після кроку 6 (DELETE) | 0 рядків |

Зупинки маршруту в порядку проходження (зв'язок N:M):

```sql
SELECT r.number, r.transport_type, rs.seq, s.name
FROM routes r
JOIN route_stops rs ON rs.route_id = r.id
JOIN stops s ON s.id = rs.stop_id
WHERE r.number = '47' AND r.transport_type = 'bus'
ORDER BY rs.seq;
```

Кількість записів у кожній таблиці (разом 157 після `init_db`):

```sql
SELECT 'routes' AS tbl, count(*) FROM routes
UNION ALL SELECT 'stops', count(*) FROM stops
UNION ALL SELECT 'route_stops', count(*) FROM route_stops
UNION ALL SELECT 'drivers', count(*) FROM drivers
UNION ALL SELECT 'vehicles', count(*) FROM vehicles;
```
