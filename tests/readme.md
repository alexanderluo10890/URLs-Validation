# Running Tests for Pokedex API

## Prerequisites

- Python 3.13
- UV package manager

## Initial Setup

1. Create and activate virtual environment:
```bash
uv venv
source .venv/bin/activate  # On Unix/macOS
# or
.\.venv\Scripts\activate  # On Windows
```

2. Install dependencies:
```bash
uv pip install -e .
```

## Running Tests

### Run All Tests
```bash
pytest
```

### Run Tests with Verbose Output
```bash
pytest -v
```

### Run Tests by Category

Run specific test files:
```bash
# Run model tests only
pytest tests/unit/test_models.py

# Run service tests only
pytest tests/unit/test_services.py

# Run file operations tests only
pytest tests/unit/test_file_operations.py
```

### Run Tests with Coverage Report
```bash
pytest --cov=app tests/
```

### Run Tests and Show Print Statements
```bash
pytest -s
```

## Test Categories

The test suite consists of 33 tests organized in three categories:
- Models (13 tests)
- Services (9 tests)
- File Operations (11 tests)

## Debugging Tests

### Show Local Variables in Failed Tests
```bash
pytest -vv --showlocals
```

### Stop on First Failure
```bash
pytest -x
```

### Get Help with pytest Commands
```bash
pytest --help
```