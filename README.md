# Advanced Traffic Analyzer

Скрипт для анализа логов веб-сервера с поддержкой фильтрации и агрегации данных.

## Описание

Инструмент командной строки для анализа логов доступа к веб-серверу. Позволяет получать детальную статистику по запросам, фильтровать данные по различным параметрам и выявлять паттерны трафика.

## Возможности

- ✅ Анализ логов в специальном формате
- ✅ Фильтрация по HTTP-методу, статус-коду и временному интервалу
- ✅ Подсчет уникальных IP-адресов
- ✅ Топ самых активных IP-адресов
- ✅ Распределение запросов по HTTP-методам
- ✅ Топ-5 наиболее запрашиваемых URL
- ✅ Анализ ошибок (4xx, 5xx)
- ✅ Статистика за последние 24 часа
- ✅ Расчет общего объема переданных данных

## Требования

- Python 3.6+
- Стандартные библиотеки Python (argparse, collections, datetime)

## Установка

```bash
# Клонируйте репозиторий или скачайте файл
git clone https://github.com/daniojey/TZREPO.git
cd traffic-analyzer

# Никаких дополнительных зависимостей устанавливать не нужно
```

## Формат входного файла

Каждая строка лог-файла должна содержать данные в следующем формате:

```
<timestamp> <ip_address> <http_method> <url> <status_code> <response_size>
```

**Пример:**
```
1717020800 192.168.1.10 GET /home 200 1500
1717020900 192.168.1.11 POST /api/login 401 120
1717021000 192.168.1.10 GET /profile 200 800
```

**Описание полей:**
- `timestamp` — Unix-время (целое число)
- `ip_address` — IPv4 адрес
- `http_method` — HTTP метод (GET, POST, PUT, DELETE, etc.)
- `url` — путь запроса
- `status_code` — HTTP статус код
- `response_size` — размер ответа в байтах

## Использование

### Базовый анализ

```bash
python advanced_traffic_analyzer.py access.log
```

### Фильтрация по HTTP-методу

```bash
python advanced_traffic_analyzer.py access.log --method GET
```

### Фильтрация по статус-коду

```bash
# Конкретный статус
python advanced_traffic_analyzer.py access.log --status 200

# Диапазон статусов
python advanced_traffic_analyzer.py access.log --status 400-499
```

### Фильтрация по временному интервалу

```bash
python advanced_traffic_analyzer.py access.log --start 1717020800 --end 1717021200
```

### Топ N самых активных IP

```bash
python advanced_traffic_analyzer.py access.log --top 10
```

### Комбинированные фильтры

```bash
python advanced_traffic_analyzer.py access.log \
  --method POST \
  --status 400-499 \
  --start 1717020800 \
  --end 1717025000 \
  --top 5
```

## Аргументы командной строки

| Аргумент | Тип | Обязательный | Описание |
|----------|-----|--------------|----------|
| `logfile` | позиционный | Да | Путь к файлу логов |
| `--method` | строка | Нет | Фильтр по HTTP-методу (GET, POST, etc.) |
| `--status` | строка/диапазон | Нет | Фильтр по статус-коду (напр. 200 или 400-499) |
| `--start` | число | Нет | Начальный timestamp для фильтрации |
| `--end` | число | Нет | Конечный timestamp для фильтрации |
| `--top` | число | Нет | Количество IP в топе (по умолчанию: 3) |

## Пример вывода

```
========================================
      TRAFFIC ANALYSIS REPORT
========================================

Filter settings:
  - Time range: all time
  - Method filter: all methods
  - Status filter: all statuses

Basic statistics:
  Total requests: 50
  Unique IPs: 15
  Total data transferred: 65890 (64.34 KB)

Request distribution:
  - GET: 68.0%
  - POST: 24.0%
  - DELETE: 4.0%
  - PUT: 2.0%
  - PATCH: 2.0%

Performance metrics:
  - Successful requests (2xx): 42
  - Client errors (4xx): 6
  - Server errors (5xx): 2
  - Average response size (2xx): 1245 bytes

Top 3 active IPs:
  1. 192.168.1.10: 12 requests
  2. 10.0.0.5: 8 requests
  3. 192.168.1.11: 7 requests

Top 5 requested URLs:
  1. /home: 9
  2. /products: 3
  3. /profile: 2
  4. /blog: 2
  5. /about: 1

Recent activity (last 24h):
  - Unique IPs: 15
  - Requests per hour: [14:00: 8, 15:00: 12, ...]
```

## Структура проекта

```
.
├── advanced_traffic_analyzer.py   # Основной скрипт
├── access.log                      # Пример лог-файла
└── README.md                       # Документация
```

## Тестирование

Создайте тестовый лог-файл `access.log` и запустите:

```bash
python advanced_traffic_analyzer.py access.log
```

## Возможные улучшения

- [ ] Поддержка других форматов логов (Apache, Nginx)
- [ ] Экспорт результатов в JSON/CSV
- [ ] Графическая визуализация данных
- [ ] Поддержка множественных лог-файлов
- [ ] Детекция аномалий и подозрительной активности

## Troubleshooting

**Ошибка: "File not found"**
- Проверьте путь к лог-файлу
- Убедитесь, что файл существует

**Ошибка: "No records found"**
- Проверьте формат лог-файла
- Убедитесь, что фильтры не слишком строгие
