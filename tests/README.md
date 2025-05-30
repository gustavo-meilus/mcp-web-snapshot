# MCP Web Snapshot Tests

This directory contains pytest tests for the MCP Web Snapshot tool.

## Test Coverage

The test suite covers the main functionality of the `website_snapshot` function with 92% code coverage:

### Test Cases

1. **`test_website_snapshot_success`**: Tests successful website snapshot capture including:

   - Accessibility snapshot parsing
   - Element reference assignment
   - Output formatting

2. **`test_website_snapshot_with_network_and_console`**: Tests monitoring capabilities:

   - Network request capture
   - Response handling
   - Console message logging

3. **`test_website_snapshot_invalid_url`**: Tests URL validation

4. **`test_website_snapshot_browser_launch_error`**: Tests error handling for browser failures

## Running Tests

```bash
# Run all tests
uv run pytest tests/

# Run with verbose output
uv run pytest tests/ -v

# Run with coverage report
PYTHONPATH=. uv run pytest tests/ --cov=src.tools.snapshot_url --cov-report=term-missing
```

## Dependencies

Test dependencies are defined in `pyproject.toml`:

- pytest
- pytest-asyncio
- pytest-mock
- pytest-cov
