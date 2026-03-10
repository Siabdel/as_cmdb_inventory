# Testing Setup and Procedures

## Testing Tools

The testing setup for this project uses the following tools:

- **Pytest**: For running tests.
- **pytest-django**: For Django-specific test utilities.
- **pytest-cov**: For generating coverage reports.
- **pytest-factoryboy**: For creating test data using factories.
- **factory-boy**: For defining test factories.
- **Faker**: For generating fake data.

## Testing Configuration

The testing configuration is defined in the `pyproject.toml` file under the `[tool.pytest.ini_options]` section. Here are the key configurations:

- **Test Options**:
  - `--reuse-db`: Reuse the database between test runs to speed up testing.
  - `--no-migrations`: Skip running database migrations during tests.
  - `--tb=short`: Use a short traceback format for test failures.
  - `--strict-markers`: Ensure all markers are defined.
  - `--strict-config`: Ensure the configuration is valid.

- **Test Paths**: Tests are located in the `tests` directory.
- **Python Files**: Test files follow the pattern `test_*.py`.
- **Python Classes**: Test classes follow the pattern `Test*`.
- **Python Functions**: Test functions follow the pattern `test_*`.
- **Markers**:
  - `unit`: Unit tests.
  - `integration`: Integration tests.
  - `api`: API endpoint tests.
  - `models`: Model tests.
  - `slow`: Slow running tests.

- **Coverage Configuration**:
  - **Source**: Coverage is measured for the `inventory` module.
  - **Omit**: Exclude migrations, tests, and management commands from coverage reports.
  - **Branch**: Measure branch coverage.
  - **Exclude Lines**: Exclude lines that match certain patterns from coverage reports.

## Running Tests

To run the tests, navigate to the project root directory and execute the following command:

```sh
pytest
```

To generate a coverage report, use the following command:

```sh
pytest --cov=inventory --cov-report=html
```

This will generate an HTML coverage report in the `htmlcov` directory.

## Best Practices

- **Use Factories**: Use `factory-boy` to create test data. This ensures that your tests are consistent and easy to maintain.
- **Use Markers**: Use the defined markers to categorize your tests. This helps in running specific types of tests.
- **Keep Tests Independent**: Ensure that each test is independent and can be run in isolation.
- **Use Mocking**: Use mocking to isolate the components being tested.
- **Write Descriptive Test Names**: Use descriptive test names to make it clear what each test is testing.
- **Run Tests Regularly**: Run tests regularly to catch issues early.
