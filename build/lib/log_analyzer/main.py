# log_analyzer_mvp/main.py
import argparse
import sys
from pathlib import Path
from collections import defaultdict
from typing import List, Dict, DefaultDict, Optional, Sequence

# Импортируем парсер из соседнего файла
from log_analyzer.log_parser import parse_log_line, LOG_LEVELS

# Тип для хранения агрегированных данных: {handler: {level: count}}
HandlerData = DefaultDict[str, DefaultDict[str, int]]

def parse_arguments(args: Optional[Sequence[str]] = None) -> argparse.Namespace:
    """Парсит аргументы командной строки."""
    parser = argparse.ArgumentParser(
        description="MVP Log Analyzer for Django logs."
    )
    parser.add_argument(
        "log_files",
        metavar="LOG_FILE",
        type=str,
        nargs='+',
        help="Path(s) to log file(s).",
    )
    parser.add_argument(
        "--report",
        type=str,
        required=True,
        choices=['handlers'], # В MVP жестко задаем единственный отчет
        help="Report name (only 'handlers' supported in MVP).",
    )
    return parser.parse_args(args)

def generate_handlers_report(data: HandlerData) -> None:
    """Генерирует и выводит отчет 'handlers' в консоль."""
    if not data:
        print("No relevant log data found for 'handlers' report.")
        return

    total_requests = sum(sum(levels.values()) for levels in data.values())
    print(f"Total requests: {total_requests}\n")

    # Простая шапка таблицы
    header = f"{'HANDLER'.ljust(40)} " # Фиксированная ширина для MVP
    for level in LOG_LEVELS:
        header += f"\t{level.rjust(8)}"
    print(header)
    print("-" * (40 + 9 * len(LOG_LEVELS))) # Простой разделитель

    level_totals: Dict[str, int] = defaultdict(int)
    # Сортируем хэндлеры по алфавиту для вывода
    sorted_handlers = sorted(data.keys())

    for handler in sorted_handlers:
        row = f"{handler.ljust(40)} "
        level_counts = data[handler]
        for level in LOG_LEVELS:
            count = level_counts.get(level, 0)
            row += f"\t{str(count).rjust(8)}"
            level_totals[level] += count
        print(row)

    # Строка с итогами
    print("-" * (40 + 9 * len(LOG_LEVELS)))
    totals_row = f"{''.ljust(40)} " # Пустое место в колонке хэндлера
    for level in LOG_LEVELS:
        totals_row += f"\t{str(level_totals[level]).rjust(8)}"
    print(totals_row)


def main() -> None:
    """Основная функция MVP."""
    args = parse_arguments()

    # Проверяем существование файлов
    log_file_paths: List[Path] = []
    for file_str in args.log_files:
        path = Path(file_str)
        if not path.is_file():
            print(f"Error: File not found: {path}", file=sys.stderr)
            sys.exit(1)
        log_file_paths.append(path)

    # В MVP поддерживается только отчет 'handlers', проверка уже сделана в argparse

    # Агрегация данных (последовательная обработка)
    aggregated_data: HandlerData = defaultdict(lambda: defaultdict(int))

    for file_path in log_file_paths:
        print(f"Processing file: {file_path}...") # Индикация прогресса
        try:
            with file_path.open('r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    parsed = parse_log_line(line)
                    if parsed:
                        handler = parsed["handler"]
                        level = parsed["level"]
                        aggregated_data[handler][level] += 1
        except IOError as e:
            print(f"Warning: Could not read file {file_path}: {e}", file=sys.stderr)
            # Продолжаем обработку других файлов

    print("Processing complete.")

    # Генерация отчета
    if args.report == 'handlers':
        generate_handlers_report(aggregated_data)
    # Другие отчеты здесь не поддерживаются в MVP

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nExecution interrupted by user.", file=sys.stderr)
        sys.exit(1)