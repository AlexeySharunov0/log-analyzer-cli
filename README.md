# Log Analyzer CLI

## Overview

Log Analyzer CLI is a command-line tool designed to parse, analyze, and generate reports from log files. It supports processing multiple log files and provides a modular architecture to extend its reporting capabilities.

## Project Structure

- `log_analyzer/` - Core application modules including:
  - `main.py` - Entry point of the application.
  - `analyzer.py` - Contains logic for analyzing parsed log data.
  - `log_parser.py` - Responsible for parsing raw log files.
  - `reporting.py` - Implements report generation based on analyzed data.
  - `utils.py` - Utility functions used across the application.
- `logs/` - Sample log files for testing and demonstration.
- `tests/` - Unit tests for different modules of the project.
- `build/` and `log_analyzer.egg-info/` - Packaging and distribution files.

## Getting Started

1. Ensure you have Python installed (version 3.7+ recommended).
2. Install any dependencies listed in `pyproject.toml` or use your preferred environment management.
3. Run the application via the command line:
   ```bash
   python -m log_analyzer.mainx
   ```
4. Provide log files located in the `logs/` directory or specify your own log files as input.

## Adding a New Report

To extend the tool with a new report, follow these steps:

1. **Create a new report class:**
   - Add a new class in `log_analyzer/reporting.py`.
   - This class should implement the logic to generate the desired report from the analyzed data.
   - Follow the existing report classes as examples for structure and methods.

2. **Integrate the new report into the analyzer:**
   - Modify `log_analyzer/analyzer.py` to include your new report class.
   - Ensure the analyzer calls your report generation logic at the appropriate stage.

3. **Update main application if needed:**
   - If your report requires new command-line options or parameters, update `log_analyzer/main.py` to handle these inputs and trigger your report.

4. **Write tests:**
   - Add unit tests for your new report class in the `tests/` directory, preferably in a new or existing test file like `test_reporting.py`.
   - Ensure your tests cover various scenarios and edge cases.

5. **Run tests:**
   - Use your preferred test runner (e.g., `pytest`) to verify all tests pass.

## Testing

The project includes unit tests for all major components located in the `tests/` directory. To run the tests:

```bash
pytest tests/
```

Ensure all tests pass before committing changes.

## Logs

Sample log files are available in the `logs/` directory for testing and demonstration purposes.

## Contributing

Contributions are welcome! Please follow the existing code style and include tests for new features.


