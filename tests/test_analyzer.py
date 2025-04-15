# tests/test_analyzer.py
import pytest
from pathlib import Path
from collections import defaultdict
from log_analyzer.analyzer import analyze_logs, _process_file_for_handlers, _merge_handler_results, HandlerData

# Убрали фикстуру fixture_path

# Используем tmp_path для создания временных файлов в тестах
def test_process_file_for_handlers_ok(tmp_path):
    """Тестирует обработку файла с корректными данными (файл создается временно)."""
    log_content = """
INFO:django.request:GET /api/v1/users/ 123 45ms
DEBUG:django.request:POST /api/v1/auth/login/ 400 15ms
WARNING:django.request:GET /admin/ 200 30ms
ERROR:django.request:PUT /api/v1/users/ 500 150ms
CRITICAL:django.request:DELETE /api/v1/users/ 503 200ms
INFO:django.server:"GET /api/v1/users/ HTTP/1.1" 200 1863
INFO:some_other_logger:This is not a request log.
DEBUG:django.request:GET /api/v1/users/ 200 55ms
INFO:django.request:GET /api/v1/items/?active=true 200 25ms
WARNING:django.request:POST /api/v1/auth/login/ 401 18ms
DEBUG:django.request:GET /admin/ 200 20ms
INFO:django.db.backends:Connection timed out
"""
    # Создаем временный файл и пишем в него контент
    file_path = tmp_path / "test_ok.log"
    file_path.write_text(log_content)

    # Вызываем тестируемую функцию с путем к временному файлу
    result = _process_file_for_handlers(file_path)

    assert isinstance(result, defaultdict)
    # Проверяем те же значения, что и раньше
    assert result["/api/v1/users/"]["INFO"] == 1
    assert result["/api/v1/users/"]["DEBUG"] == 1 # Было 2 запроса DEBUG к users
    assert result["/api/v1/users/"]["ERROR"] == 1
    assert result["/api/v1/users/"]["CRITICAL"] == 1
    assert result["/api/v1/auth/login/"]["DEBUG"] == 1
    assert result["/api/v1/auth/login/"]["WARNING"] == 1
    assert result["/admin/"]["WARNING"] == 1
    assert result["/admin/"]["DEBUG"] == 1 # Было 2 запроса DEBUG к admin
    assert result["/api/v1/items/"]["INFO"] == 1
    assert "INFO:django.server" not in result

def test_process_file_for_handlers_empty(tmp_path):
    """Тестирует обработку пустого файла (файл создается временно)."""
    file_path = tmp_path / "empty.log"
    file_path.touch() # Создаем пустой файл
    result = _process_file_for_handlers(file_path)
    assert isinstance(result, defaultdict)
    assert not result

def test_process_file_for_handlers_malformed(tmp_path):
    """Тестирует обработку файла с некорректными данными (файл создается временно)."""
    log_content = """
INFO django.request GET /api/v1/users/ 123 45ms
DEBUG:django.request No path here
WARNING:some_logger:Some random message
"""
    file_path = tmp_path / "malformed.log"
    file_path.write_text(log_content)
    result = _process_file_for_handlers(file_path)
    assert isinstance(result, defaultdict)
    assert not result

# Тест _merge_handler_results не меняется, он не использовал файлы
def test_merge_handler_results():
    """Тестирует слияние результатов из нескольких словарей."""
    # <<< КОД ОСТАЕТСЯ ПРЕЖНИМ >>>
    dict1: HandlerData = defaultdict(lambda: defaultdict(int))
    dict1["/path1"]["INFO"] = 10
    dict1["/path1"]["DEBUG"] = 5
    dict1["/path2"]["INFO"] = 2

    dict2: HandlerData = defaultdict(lambda: defaultdict(int))
    dict2["/path1"]["INFO"] = 7 # Добавляется к существующему
    dict2["/path2"]["WARNING"] = 3 # Новый уровень для path2
    dict2["/path3"]["ERROR"] = 1 # Новый путь

    dict_empty: HandlerData = defaultdict(lambda: defaultdict(int))

    merged = _merge_handler_results([dict1, dict2, dict_empty])

    assert merged["/path1"]["INFO"] == 17
    assert merged["/path1"]["DEBUG"] == 5
    assert merged["/path2"]["INFO"] == 2
    assert merged["/path2"]["WARNING"] == 3
    assert merged["/path3"]["ERROR"] == 1
    assert len(merged) == 3 # Убедимся, что нет лишних ключей


def test_analyze_logs_single_file(tmp_path, capsys):
    """Тестирует analyze_logs с одним временным файлом."""
    log_content = "INFO:django.request:GET /path1 1 1ms\nDEBUG:django.request:POST /path1 2 2ms"
    file_path = tmp_path / "analyze_test.log"
    file_path.write_text(log_content)
    log_files = [file_path]

    result = analyze_logs(log_files, "handlers")
    captured = capsys.readouterr() # Перехватываем stdout

    assert "Analyzing for 'handlers':" in captured.out
    assert "Analysis complete." in captured.out
    assert result["/path1"]["INFO"] == 1
    assert result["/path1"]["DEBUG"] == 1

def test_analyze_logs_multiple_files(tmp_path, capsys):
    """Тестирует analyze_logs с несколькими временными файлами."""
    log_content1 = "INFO:django.request:GET /path1 1 1ms\n"
    log_content2 = "DEBUG:django.request:POST /path1 2 2ms\n"
    log_content_bad = "GARBAGE LINE\n"

    f1 = tmp_path / "multi1.log"
    f2 = tmp_path / "multi2.log"
    f3 = tmp_path / "multi_bad.log"
    f1.write_text(log_content1)
    f2.write_text(log_content2)
    f3.write_text(log_content_bad)

    log_files = [f1, f2, f3, f1] # Обрабатываем первый файл дважды, плохой файл игнорируется
    result = analyze_logs(log_files, "handlers")
    captured = capsys.readouterr()

    assert captured.out.count("Analyzing for 'handlers':") == 4 # 4 файла передано
    assert "Analysis complete." in captured.out
    # Данные должны удвоиться для path1 INFO и появиться DEBUG
    assert result["/path1"]["INFO"] == 2
    assert result["/path1"]["DEBUG"] == 1
    assert len(result) == 1 # Только один хэндлер '/path1' должен быть

def test_analyze_logs_unknown_report_type(tmp_path, capsys):
    """Тестирует analyze_logs с неизвестным типом отчета (файл не важен)."""
    f1 = tmp_path / "dummy.log"
    f1.touch()
    log_files = [f1]
    result = analyze_logs(log_files, "unknown_report")
    captured = capsys.readouterr()

    assert result is None
    assert "Warning: Analysis logic for report type 'unknown_report'" in captured.err