import sys
from collections import defaultdict
from typing import List, Dict, DefaultDict, Any
from pathlib import Path
from .log_parser import parse_log_line
from .utils import LOG_LEVELS


HandlerData = DefaultDict[str, DefaultDict[str, int]] 

#  Функции для отчета 'handlers'
def _process_file_for_handlers(file_path: Path) -> HandlerData:
    """
    Обрабатывает один файл, собирая данные для отчета 'handlers'.
    (Внутренняя функция, специфичная для 'handlers')
    """
    handler_counts: HandlerData = defaultdict(lambda: defaultdict(int))
    print(f"Analyzing for 'handlers': {file_path}...") # Индикация
    try:
        with file_path.open('r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                parsed_data = parse_log_line(line)
                if parsed_data and "handler" in parsed_data and "level" in parsed_data:
                    handler = parsed_data["handler"]
                    level = parsed_data["level"]
                    handler_counts[handler][level] += 1
    except IOError as e:
        print(f"Warning: Could not read file {file_path}: {e}", file=sys.stderr)
    return handler_counts

def _merge_handler_results(results_list: List[HandlerData]) -> HandlerData:
    """
    Объединяет результаты обработки нескольких файлов для отчета 'handlers'.
    (Внутренняя функция, специфичная для 'handlers')
    """
    merged: HandlerData = defaultdict(lambda: defaultdict(int))
    for result_dict in results_list:
        for handler, level_counts in result_dict.items():
            for level, count in level_counts.items():
                merged[handler][level] += count
    return merged

def analyze_logs(log_files: List[Path], report_type: str) -> Any:
    """
    Анализирует логи для указанного типа отчета.
    В будущем может вызывать разные функции обработки в зависимости от report_type.
    """
    results = []
    if report_type == 'handlers':
        for file_path in log_files:
            results.append(_process_file_for_handlers(file_path))
        print("Analysis complete.")
        return _merge_handler_results(results)

    else:
        # Если тип отчета неизвестен на этапе анализа (хотя он проверяется в main)
        print(f"Warning: Analysis logic for report type '{report_type}' is not implemented.", file=sys.stderr)
        return None # Или пустая структура данных