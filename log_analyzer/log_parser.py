import re
from typing import Optional, Dict

# Уровни логирования 
LOG_LEVELS: list[str] = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

# Regex для захвата уровня, логгера и сообщения
LOG_LINE_RE = re.compile(r"^(DEBUG|INFO|WARNING|ERROR|CRITICAL):(?P<logger>[^:]+):(?P<message>.*)")
# Regex для поиска пути в сообщении django.request
REQUEST_PATH_RE = re.compile(r"\s+(/[^ ]*)\s+")  # Захватывает путь с параметрами запроса

def parse_log_line(line: str) -> Optional[Dict[str, str]]:
    """
    Парсит строку лога для извлечения уровня и хэндлера из django.request.

    Args:
        line: Строка лога.

    Returns:
        Словарь {'level': УРОВЕНЬ, 'handler': ПУТЬ} или None.
    """
    match = LOG_LINE_RE.match(line)
    if not match:
        return None

    data = match.groupdict()
    level = match.groups()[0] # Уровень логирования
    logger = data.get("logger")
    message = data.get("message", "").strip()

    # Интересуют только логи django.request
    if logger == "django.request":
        path_match = REQUEST_PATH_RE.search(message)
        if path_match:
            handler = path_match.group(1)
            # Убираем параметры запроса из пути
            handler = handler.split('?')[0]
            # Возвращаем только нужные для отчета 'handlers' данные
            if level in LOG_LEVELS:
                 return {"level": level, "handler": handler}
            # else: # Можно добавить логирование неизвестных уровней при необходимости
            #    print(f"Warning: Unknown log level '{level}' in line: {line.strip()}", file=sys.stderr)

    return None # Игнорируем остальные строки
