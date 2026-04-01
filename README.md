# Решения задач по веб-разработке

Собраны решения пяти практических задач по проектированию API, работе с базами данных и валидации.

## Задача 1. База данных интернет-магазина

**Условие:** спроектировать базу данных для интернет-магазина (пользователи, товары, заказы). Написать запрос для вывода заказов пользователя с суммой по заказу.

### Схема таблиц

**Users**
- id (PK) — идентификатор пользователя
- email — email пользователя (обязательное, уникальное)
- hashed_password — хеш пароля (обязательное)
- full_name — полное имя
- created_at — дата регистрации

**Products**
- id (PK) — идентификатор товара
- name — название товара (обязательное)
- price — цена (обязательное)
- stock_quantity — остаток на складе (обязательное)

**Orders**
- id (PK) — номер заказа
- user_id (FK → Users.id) — покупатель (обязательное)
- order_date — дата заказа
- status — статус заказа (pending, paid, shipped, delivered, cancelled)
- total_amount — общая сумма заказа

**OrderItems**
- id (PK) — идентификатор позиции
- order_id (FK → Orders.id) — заказ (обязательное)
- product_id (FK → Products.id) — товар (обязательное)
- quantity — количество (обязательное)
- price_at_moment — цена на момент заказа (обязательное)

Поле price_at_moment нужно, чтобы при изменении цены товара исторические заказы не искажались.

### Запрос на вывод заказов пользователя с суммой

```sql
SELECT 
    o.id,
    o.order_date,
    o.status,
    COALESCE(SUM(oi.quantity * oi.price_at_moment), 0) AS total_sum
FROM orders o
LEFT JOIN order_items oi ON o.id = oi.order_id
WHERE o.user_id = 1
GROUP BY o.id
ORDER BY o.order_date DESC;
```

LEFT JOIN используется, чтобы показать заказы без товаров (сумма 0). COALESCE заменяет NULL на 0.

---

## Задача 2. CRUD для товаров

**Условие:** реализовать CRUD-функционал для сущности "товар" (название, цена, остаток). Описать маршруты, методы, валидацию и поток данных.

### Маршруты и HTTP методы

| Метод | URL | Описание |
|-------|-----|----------|
| GET | /products/ | Список товаров |
| POST | /products/ | Создание товара |
| GET | /products/{id}/ | Детали товара |
| PUT | /products/{id}/ | Полное обновление |
| PATCH | /products/{id}/ | Частичное обновление |
| DELETE | /products/{id}/ | Удаление товара |

### Модель

```python
class Product(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

### Валидация

Валидация происходит в сериализаторе. Проверяются:
- цена должна быть больше 0
- остаток не может быть отрицательным

```python
def validate_price(self, value):
    if value <= 0:
        raise ValidationError("Цена должна быть больше 0")
    return value
```

### Поток данных

1. Клиент отправляет HTTP запрос
2. Маршрутизатор направляет запрос во view
3. View передает данные в сериализатор
4. Сериализатор валидирует данные
5. При успешной валидации данные сохраняются в БД
6. Сериализатор преобразует объект в JSON
7. View возвращает HTTP ответ

### Почему валидация нужна на сервере

Клиентскую валидацию можно обойти (отключить JavaScript, отправить запрос через curl). Серверная валидация — единственная надежная защита от некорректных данных.

---

## Задача 3. Форма регистрации с валидацией

**Условие:** описать проверки формы регистрации на клиенте и сервере. Объяснить, какие проверки обязательно дублировать и почему.

---
<img width="678" height="678" alt="изображение" src="https://github.com/user-attachments/assets/fb32731a-59da-4d52-8fe2-073efe9f498f" />

---

### Проверки на клиенте (JavaScript)

- поля не пустые
- email содержит @
- пароль минимум 8 символов
- пароль содержит заглавную букву, строчную букву и цифру
- пароль и подтверждение совпадают
- визуальная обратная связь (подсветка требований)

### Проверки на сервере (Django DRF)

- все проверки сложности пароля (дублируются)
- уникальность username и email
- совпадение паролей
- обязательность полей

### Почему проверки нужно дублировать

| Проверка | На клиенте | На сервере | Причина |
|----------|------------|------------|---------|
| сложность пароля | для удобства | обязательно | клиент можно обойти |
| уникальность email | опционально | обязательно | только сервер знает о других пользователях |
| совпадение паролей | для быстрой реакции | обязательно | защита от подделки запроса |

Клиентские проверки улучшают用户体验, но не защищают от злонамеренных запросов. Серверные проверки — единственный способ гарантировать корректность данных.

---

## Задача 4. API агрегатора отелей

**Условие:** описать API для поиска отелей с фильтрацией по городу и цене. Объяснить формат ответа, обработку на сервере и использование на фронтенде.

---

<img width="1247" height="612" alt="изображение" src="https://github.com/user-attachments/assets/70dc4dfa-92c7-4d8f-953f-f9f7852a8217" />

---

### Что возвращает сервер

Запрос: `GET /api/hotels?city=Москва&min_price=3000&max_price=7000`

Ответ:
```json
{
    "count": 2,
    "results": [
        {
            "id": 1,
            "name": "Отель Арбат",
            "city": "Москва",
            "address": "ул. Арбат, 10",
            "price_per_night": "4500.00",
            "rating": 4.5
        },
        {
            "id": 2,
            "name": "Гостиница Метрополь",
            "city": "Москва",
            "address": "Театральный пр-д, 2",
            "price_per_night": "6800.00",
            "rating": 4.8
        }
    ]
}
```

### Обработка на сервере

```python
class HotelListView(generics.ListAPIView):
    def get_queryset(self):
        queryset = Hotel.objects.all()
        
        city = self.request.query_params.get('city')
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        
        if city:
            queryset = queryset.filter(city__iexact=city)
        if min_price:
            queryset = queryset.filter(price_per_night__gte=min_price)
        if max_price:
            queryset = queryset.filter(price_per_night__lte=max_price)
        
        return queryset.order_by('price_per_night')
```

Параметры извлекаются из query string. Каждый параметр опциональный. Результаты сортируются по цене.

### Использование на фронтенде

```javascript
async function searchHotels() {
    const city = document.getElementById('city').value;
    const minPrice = document.getElementById('min_price').value;
    const maxPrice = document.getElementById('max_price').value;
    
    const params = new URLSearchParams();
    if (city) params.append('city', city);
    if (minPrice) params.append('min_price', minPrice);
    if (maxPrice) params.append('max_price', maxPrice);
    
    const response = await fetch(`/api/hotels/?${params}`);
    const data = await response.json();
    
    displayHotels(data.results);
}
```

Фронтенд собирает значения из полей ввода, формирует query string и отправляет GET-запрос. Полученные данные отображаются в виде карточек.

---

## Задача 5. Расписание занятий

**Условие:** спроектировать модуль расписания учебного заведения. Перечислить основные сущности. Описать, как избежать конфликтов (группа в двух местах, преподаватель в двух местах одновременно).

### Основные сущности

- **Group** — учебная группа (название, курс)
- **Teacher** — преподаватель (ФИО, email)
- **Classroom** — аудитория (здание, номер, вместимость)
- **Course** — учебный курс (название, количество часов)
- **Schedule** — расписание (связывает все сущности + время)

### Как избежать конфликтов

Конфликты проверяются на двух уровнях:

**1. На уровне базы данных (уникальные ограничения)**

```python
UniqueConstraint('classroom_id', 'day_of_week', 'start_time', 'semester')
UniqueConstraint('teacher_id', 'day_of_week', 'start_time', 'semester')
UniqueConstraint('group_id', 'day_of_week', 'start_time', 'semester')
```

Это гарантирует, что в одной аудитории не будет двух занятий, начинающихся в одно время. Аналогично для преподавателя и группы.

**2. На уровне приложения (проверка пересечений)**

```python
def check_conflicts(db, schedule):
    # ищем занятия, которые пересекаются по времени
    conflicts = db.query(Schedule).filter(
        Schedule.day_of_week == schedule.day_of_week,
        Schedule.start_time < schedule.end_time,
        Schedule.end_time > schedule.start_time
    ).all()
    
    return conflicts
```

Проверка `start_time < new.end_time AND end_time > new.start_time` находит все пересечения (частичные и полные), а не только точное совпадение времени начала.

### Почему два уровня

- **База данных** защищает от конкурентных запросов (когда два пользователя одновременно пытаются создать занятие)
- **Приложение** дает понятные сообщения об ошибках (какой именно преподаватель и в какое время уже занят)

---
