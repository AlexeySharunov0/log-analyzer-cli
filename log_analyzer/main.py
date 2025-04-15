import argparse
import sys
from pathlib import Path
from typing import List

from log_analyzer.analyzer import analyze_logs
from log_analyzer.reporting import get_report_generator

def parse_arguments(args: List[str] = None) -> argparse.Namespace:
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
        choices=['handlers'],  # В MVP жестко задаем единственный отчет
        help="Report name (only 'handlers' supported in MVP).",
    )
    return parser.parse_args(args)

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

    try:
        # Анализ логов через analyze_logs
        aggregated_data = analyze_logs(log_file_paths, args.report)

        # Получаем генератор отчета
        report_generator = get_report_generator(args.report)
        # Генерируем отчет
        report_generator.generate(aggregated_data)

    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExecution interrupted by user.", file=sys.stderr)
        sys.exit(1)
