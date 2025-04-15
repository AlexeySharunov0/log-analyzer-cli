import pytest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

from log_analyzer.main import parse_arguments, main

def test_parse_arguments_ok(tmp_path):
    f1 = tmp_path / "f1.log"
    f2 = tmp_path / "f2.log"
    args_list = [str(f1), str(f2), "--report", "handlers"]
    parsed_args = parse_arguments(args_list)
    assert parsed_args.log_files == [str(f1), str(f2)]
    assert parsed_args.report == "handlers"

def test_parse_arguments_missing_report():
    with pytest.raises(SystemExit):
        parse_arguments(["file1.log"])

def test_parse_arguments_invalid_report():
    with pytest.raises(SystemExit):
        parse_arguments(["file1.log", "--report", "invalid_report_name"])

def test_parse_arguments_no_files():
    with pytest.raises(SystemExit):
        parse_arguments(["--report", "handlers"])

@patch('log_analyzer.main.parse_arguments')
@patch('log_analyzer.main.analyze_logs')
@patch('log_analyzer.main.get_report_generator')
def test_main_flow_ok(mock_get_generator, mock_analyze, mock_parse_args, tmp_path):
    f1 = tmp_path / "main_ok1.log"
    f2 = tmp_path / "main_ok2.log"
    f1.touch()
    f2.touch()

    mock_parse_args.return_value = MagicMock(log_files=[str(f1), str(f2)], report="handlers")
    mock_analyze.return_value = {"some": "data"}
    mock_report_instance = MagicMock()
    mock_get_generator.return_value = mock_report_instance

    main()

    mock_parse_args.assert_called_once()
    assert mock_analyze.called, "Функция analyze_logs не была вызвана"
    analyze_call_args = mock_analyze.call_args[0]
    assert isinstance(analyze_call_args[0], list)
    assert all(isinstance(p, Path) for p in analyze_call_args[0])
    assert analyze_call_args[0][0] == f1
    assert analyze_call_args[0][1] == f2
    assert analyze_call_args[1] == "handlers"
    mock_analyze.assert_called_once()
    mock_get_generator.assert_called_once_with("handlers")
    mock_report_instance.generate.assert_called_once_with({"some": "data"})

@patch('log_analyzer.main.parse_arguments')
def test_main_file_not_found(mock_parse_args):
    mock_parse_args.return_value = MagicMock(log_files=["non_existent_file.log"], report="handlers")
    with pytest.raises(SystemExit) as e:
        main()
    assert e.value.code == 1

@patch('log_analyzer.main.parse_arguments')
@patch('log_analyzer.main.analyze_logs')
@patch('log_analyzer.main.get_report_generator')
def test_main_analysis_error(mock_get_generator, mock_analyze, mock_parse_args, tmp_path):
    f1 = tmp_path / "dummy_ae.log"
    f1.touch()
    mock_parse_args.return_value = MagicMock(log_files=[str(f1)], report="handlers")
    mock_analyze.side_effect = ValueError("Analysis failed!")

    with pytest.raises(SystemExit) as e:
        main()
    assert e.value.code == 1
    mock_get_generator.assert_not_called()

@patch('log_analyzer.main.parse_arguments')
@patch('log_analyzer.main.analyze_logs')
@patch('log_analyzer.main.get_report_generator')
def test_main_reporting_error(mock_get_generator, mock_analyze, mock_parse_args, tmp_path):
    f1 = tmp_path / "dummy_re.log"
    f1.touch()
    mock_parse_args.return_value = MagicMock(log_files=[str(f1)], report="handlers")
    mock_analyze.return_value = {"some": "data"}
    mock_report_instance = MagicMock()
    mock_report_instance.generate.side_effect = ValueError("Reporting failed!")
    mock_get_generator.return_value = mock_report_instance

    with pytest.raises(SystemExit) as e:
        main()
    assert e.value.code == 1
    mock_report_instance.generate.assert_called_once()
