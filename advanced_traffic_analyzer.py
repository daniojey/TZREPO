import argparse
from collections import Counter, defaultdict
from datetime import datetime
import sys
from traceback import print_tb


parser = argparse.ArgumentParser(
                    prog='LogParcerName',
                    description='Parse request-response log',
        )

parser.add_argument('--method', help="Filter http method")
parser.add_argument('--status', help="Filter status_code")
parser.add_argument('--start', type=int, help='Filter start time')
parser.add_argument('--end', type=int, help='Filter end time')
parser.add_argument('--top', type=int, default=3, help="Rating")


def bytes_to_human(bytes_num):
    """Конвертирует байты в человекочитаемый формат"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_num < 1024.0:
            return f"{bytes_num:.2f} {unit}"
        bytes_num /= 1024.0
    return f"{bytes_num:.2f} PB"

def parse_line(line):
    """Разбираем линию и возвращаем словарь"""
    line = line.strip().split()
    if len(line) < 6:
        return None

    return {
        'timestamp': int(line[0]),
        'ip': line[1],
        'method': line[2],
        'url': line[3],
        'status': int(line[4]),
        'size': int(line[5])
    }

def matches_filters(record, args):
    """Проверяет, подходит ли запись под фильтры"""
    # Фильтр по методу
    if args.method and record['method'] != args.method:
        return False
    
    # Фильтр по времени
    if args.start and record['timestamp'] < args.start:
        return False
    if args.end and record['timestamp'] > args.end:
        return False
    
    # Фильтр по статусу
    if args.status:
        if '-' in args.status:
            # Диапазон статусов
            start_status, end_status = map(int, args.status.split('-'))
            if not (start_status <= record['status'] <= end_status):
                return False
        else:
            # Конкретный статус
            if record['status'] != int(args.status):
                return False
    
    return True

def collect_statistic(records, args):
    "Собирает статистику на основе полученых отфильтрованных данных"
    stats = {}

    total = len(records)

    # Определяем базовые данные
    stats['total_requests'] = total
    stats['unique_ips'] = len(set(r['ip'] for r in records))
    stats['total_data'] = sum(r['size'] for r in records)

    # Подсчитываем ips для топа
    ip_counter = Counter(r['ip'] for r in records)
    stats['top_ips'] = ip_counter.most_common(args.top)

    # Подсчитываем методи и % их использования
    method_counter = Counter(r['method'] for r in records)
    stats['method_distribution'] = {
        method: (count / total * 100)
        for method, count in method_counter.items()
    }

    # Подсчитываем 5 популярных urls
    url_counter = Counter(r['url'] for r in records)
    stats['top_urls'] = url_counter.most_common(5)

    # Считаем статистику статусов
    stats['status_2xx'] = sum(1 for r in records if 200 <= r['status'] < 300)
    stats['status_4xx'] = sum(1 for r in records if 400 <= r['status'] < 500)
    stats['status_5xx'] = sum(1 for r in records if 500 <= r['status'] < 600)

    # Считаем средний размер ответа для 2xx статусов
    sucessful = [r['size'] for r in records if 200 <= r['status'] < 300]
    stats['avg_size_2xx'] = sum(sucessful) / len(sucessful) if sucessful else 0

    if records:
        max_timestamp = max(r['timestamp'] for r in records)
        last_24h = [r for r in records if r['timestamp'] > max_timestamp - 86400]
        stats['unique_ips_24h'] = len(set(r['ip'] for r in last_24h))
        
        # Запросы по часам
        hours_counter = defaultdict(int)
        for r in last_24h:
            hour = datetime.fromtimestamp(r['timestamp']).hour
            hours_counter[hour] += 1
        stats['requests_per_hour'] = dict(sorted(hours_counter.items()))
    else:
        stats['unique_ips_24h'] = 0
        stats['requests_per_hour'] = {}

    return stats

def parse_log_file(args):
    """ Основная точка скрипта которая парсит файл логов"""
    records = []
    
    # Парсим файл
    try:
        with open('sample_access.log', 'r') as f:
            for line in f:
                record = parse_line(line)
                if record and matches_filters(record, args):
                    records.append(record)
    except FileNotFoundError:
        print(f"Error: File sample_access.log not found")
        sys.exit(1)
    
    if not records:
        print("No records found matching the filters")
        return
    
    stats = collect_statistic(records, args)

    print_results(stats, args)


def print_results(stats,args):
    """Выводит отчет в требуемом формате"""
    print("=" * 40)
    print("TRAFFIC ANALYSIS REPORT".center(40))
    print("=" * 40)
    print()
    
    # Настройки фильтров
    print("Filter settings:")
    if args.start or args.end:
        start_str = datetime.fromtimestamp(args.start).strftime('%Y-%m-%d %H:%M:%S') if args.start else 'beginning'
        end_str = datetime.fromtimestamp(args.end).strftime('%Y-%m-%d %H:%M:%S') if args.end else 'end'
        print(f"  - Time range: {start_str} - {end_str}")
    else:
        print("  - Time range: all time")
    
    print(f"  - Method filter: {args.method or 'all methods'}")
    print(f"  - Status filter: {args.status or 'all statuses'}")
    print()
    
    # Базовая статистика
    print("Basic statistics:")
    print(f"  Total requests: {stats['total_requests']}")
    print(f"  Unique IPs: {stats['unique_ips']}")
    print(f"  Total data transferred: {stats['total_data']} ({bytes_to_human(stats['total_data'])})")
    print()
    
    # Распределение по методам
    print("Request distribution:")
    for method, percentage in sorted(stats['method_distribution'].items()):
        print(f"  - {method}: {percentage:.1f}%")
    print()
    
    # Метрики производительности
    print("Performance metrics:")
    print(f"  - Successful requests (2xx): {stats['status_2xx']}")
    print(f"  - Client errors (4xx): {stats['status_4xx']}")
    print(f"  - Server errors (5xx): {stats['status_5xx']}")
    print(f"  - Average response size (2xx): {stats['avg_size_2xx']:.0f} bytes")
    print()
    
    # Топ IP
    print(f"Top {args.top} active IPs:")
    for i, (ip, count) in enumerate(stats['top_ips'], 1):
        print(f"  {i}. {ip}: {count} requests")
    print()
    
    # Топ URL
    print("Top 5 requested URLs:")
    for i, (url, count) in enumerate(stats['top_urls'], 1):
        print(f"  {i}. {url}: {count}")
    print()
    
    # Активность за 24 часа
    print("Recent activity (last 24h):")
    print(f"  - Unique IPs: {stats['unique_ips_24h']}")
    if stats['requests_per_hour']:
        hours_str = ', '.join(f"{h:02d}:00: {c}" for h, c in stats['requests_per_hour'].items())
        print(f"  - Requests per hour: [{hours_str}]")
    print()


if __name__ == '__main__':
    args = parser.parse_args()
    parse_log_file(args)