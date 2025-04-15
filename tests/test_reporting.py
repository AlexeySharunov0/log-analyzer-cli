import pytest
from io import StringIO
import sys
from collections import defaultdict

from log_analyzer.reporting import (
    HandlersReport,
    get_report_generator,
    get_available_report_names,
    AVAILABLE_REPORTS,
    BaseReport 
)
from log_analyzer.analyzer import HandlerData 

# Фикстура для тестовых данных 
@pytest.fixture
def sample_handler_data() -> HandlerData:
    data: HandlerData = defaultdict(lambda: defaultdict(int))
    data["/api/users"]["INFO"] = 15
    data["/api/users"]["DEBUG"] = 5
    data["/admin"]["WARNING"] = 3
    data["/admin"]["ERROR"] = 1
    data["/api/items"]["CRITICAL"] = 2
    return data

def test_handlers_report_generation(sample_handler_data, capsys):
    report = HandlersReport()
    report.generate(sample_handler_data)
    captured = capsys.readouterr()
    output = captured.out

    assert "Total requests: 26" in output 
    assert "HANDLER" in output
    assert "DEBUG" in output


def test_handlers_report_empty_data(capsys):
    report = HandlersReport()
    empty_data: HandlerData = defaultdict(lambda: defaultdict(int))
    report.generate(empty_data)
    captured = capsys.readouterr()
    assert "No relevant log data found" in captured.out

def test_get_report_generator():
    handlers_gen = get_report_generator("handlers")
    assert isinstance(handlers_gen, HandlersReport)

def test_get_available_report_names():
    names = get_available_report_names()
    assert isinstance(names, list)