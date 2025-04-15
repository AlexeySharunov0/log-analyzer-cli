from abc import ABC, abstractmethod
from typing import Dict, List, Any, DefaultDict, Optional
from collections import defaultdict
from .utils import LOG_LEVELS
from .analyzer import HandlerData # Импортируем тип данных от анализатора


class BaseReport(ABC):
    """Абстрактный базовый класс для генераторов отчетов."""

    @abstractmethod
    def generate(self, data: Any) -> None:
        """
        Метод для генерации и вывода отчета.
        Тип 'data' может отличаться для разных отчетов.
        """
        pass

class HandlersReport(BaseReport):
    """Генерирует отчет о состоянии ручек API по уровням логирования."""

    def generate(self, data: HandlerData) -> None:
        """
        Форматирует и выводит отчет 'handlers' в консоль.
        Принимает данные типа HandlerData.
        """
        if not data:
            print("No relevant log data found for 'handlers' report.")
            return

        total_requests = sum(sum(levels.values()) for levels in data.values())
        print(f"Total requests: {total_requests}\n")

        max_handler_len = max(len(h) for h in data.keys()) if data else 10
        header_len = max(len("HANDLER"), max_handler_len)
        level_width = 8 # Фиксированная ширина для уровней

        header = f"{'HANDLER'.ljust(header_len)} "
        for level in LOG_LEVELS:
            header += f"\t{level.rjust(level_width)}"
        print(header)
        print("-" * len(header.expandtabs(level_width)))

        level_totals: Dict[str, int] = defaultdict(int)
        sorted_handlers = sorted(data.keys())

        for handler in sorted_handlers:
            row = f"{handler.ljust(header_len)} "
            level_counts = data[handler]
            for level in LOG_LEVELS:
                count = level_counts.get(level, 0)
                row += f"\t{str(count).rjust(level_width)}"
                level_totals[level] += count
            print(row)

        print("-" * len(header.expandtabs(level_width)))
        totals_row = f"{''.ljust(header_len)} "
        for level in LOG_LEVELS:
            totals_row += f"\t{str(level_totals[level]).rjust(level_width)}"
        print(totals_row)



AVAILABLE_REPORTS: Dict[str, BaseReport] = {
    "handlers": HandlersReport(),
    # "error_summary": ErrorSummaryReport(), # Пример добавления нового
}

def get_report_generator(report_name: str) -> Optional[BaseReport]:
    """
    Возвращает объект генератора отчета по его имени из реестра.
    """
    return AVAILABLE_REPORTS.get(report_name)

def get_available_report_names() -> List[str]:
    """Возвращает список имен доступных отчетов."""
    return list(AVAILABLE_REPORTS.keys())