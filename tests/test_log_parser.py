import pytest
from log_analyzer.log_parser import parse_log_line

@pytest.mark.parametrize(
    "line, expected",
    [
        ("INFO:django.request:GET /api/v1/users/ 123 45ms", {"level": "INFO", "handler": "/api/v1/users/"}),
        ("DEBUG:django.request:POST /api/v1/auth/login/ 400 15ms", {"level": "DEBUG", "handler": "/api/v1/auth/login/"}),
        ("WARNING:django.request:GET /admin/ 200 30ms", {"level": "WARNING", "handler": "/admin/"}),
        ("ERROR:django.request:PUT /api/v1/users/ 500 150ms", {"level": "ERROR", "handler": "/api/v1/users/"}),
        ("CRITICAL:django.request:DELETE /api/v1/users/ 503 200ms", {"level": "CRITICAL", "handler": "/api/v1/users/"}),
        ("INFO:django.request:GET /api/v1/items/?active=true 200 25ms", {"level": "INFO", "handler": "/api/v1/items/"}), # Проверка пути с параметрами
    ],
)
def test_parse_log_line_valid(line, expected):
    """Тестирует парсинг корректных строк django.request."""
    assert parse_log_line(line) == expected

@pytest.mark.parametrize(
    "line",
    [
        "INFO:django.server:\"GET /api/v1/users/ HTTP/1.1\" 200 1863", 
        "INFO:some_other_logger:This is not a request log.", 
        "DEBUG:django.request No path here", 
        "WARNING:django.request:", 
        "INFO django.request GET /api/v1/users/ 123 45ms", 
        "Just some random text", 
        "", 
    ],
)
def test_parse_log_line_invalid_or_irrelevant(line):
    """Тестирует строки, которые не должны парситься как валидный запрос."""
    assert parse_log_line(line) is None