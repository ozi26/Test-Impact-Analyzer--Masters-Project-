# Configuration-Aware Test Impact Analyzer for Micro-service Applications

## 1. Project purpose

This project is a Python research prototype for a **Configuration-Aware Test Impact Analyzer (TIA)**.

It detects:

1. Source-code changes.
2. Runtime configuration changes.
3. Tests that are affected by those changes.

The important improvement is that configuration is treated as part of runtime behavior. A change such as `inventory.retry.attempts: 2` to `inventory.retry.attempts: 5` can affect a test even when source code does not change.

## 2. Main flow

```text
Developer Change
       |
       v
Git Change Detector
       |
       +----------------------+
       |                      |
       v                      v
Source Change Parser     Config Change Parser
       |                      |
       +----------+-----------+
                  |
                  v
          Runtime Trace Map
                  |
                  v
            Impact Mapping
                  |
                  v
            Test Selection
                  |
                  v
                  CI
```

## 3. What each part does

### Source-code changes

Git compares two revisions and returns added and removed source lines. The analyzer extracts words from those exact changed lines and uses them to rank tests with the lexical method.

### Configuration changes

The analyzer parses YAML/YML, JSON, Java properties, and XML. Nested settings are converted into dotted keys and the old/new values are compared exactly.

### Runtime configuration mapping

OpenTelemetry records the exact configuration file and key accessed during a test. The records are stored in `trace-map.json`, so no database is required.

### Test selection

A test can be selected because:

- Its source text matches changed terms.
- Its runtime trace shows that it used an exact changed configuration key.
- Both methods select it.

## 4. Important Objective 3 point

OpenTelemetry does **not automatically know the semantic configuration key used by arbitrary application code**.

The application must expose that access to the tracing layer. This project demonstrates that with:

```python
record_config_access(
    "sample_microservices/order_service/config.yaml",
    "inventory.retry.attempts",
)
```

This creates the relationship:

```text
Test
  -> Microservice
      -> Configuration file
          -> Exact configuration key
```

For a real microservice application, a small instrumentation hook or wrapper should be added where the application reads the configuration value.

## 5. No database

This implementation deliberately uses no database. The runtime dependency map is stored in `trace-map.json`.

## 6. Project structure

```text
config_aware_tia_v2/
├── analyzer/
│   ├── __init__.py
│   ├── constants.py
│   ├── text_utils.py
│   ├── file_detector.py
│   ├── config_parser.py
│   ├── git_changes.py
│   ├── lexical_selector.py
│   ├── tracing.py
│   ├── trace_store.py
│   ├── telemetry.py
│   ├── config_selection.py
│   ├── analyzer.py
│   └── cli.py
├── tests/
│   ├── test_analyzer.py
│   ├── test_runtime_selection.py
│   ├── test_tracing.py
│   ├── test_source_diff.py
│   ├── test_checkout.py
│   ├── test_inventory.py
│   └── test_pricing.py
├── sample_microservices/
│   ├── order_service/
│   ├── inventory_service/
│   ├── pricing_service/
│   └── run_traced_tests.py
├── .github/workflows/tia.yml
├── Jenkinsfile
├── requirements.txt
├── .gitignore
└── README.md
```

## 7. Requirements

- Python 3.12 or newer.
- Git.
- pip.

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

## 8. First test: run all unit tests

```bash
pytest -q
```

All tests should pass.

## 9. Second test: create the runtime trace map

```bash
python sample_microservices/run_traced_tests.py
```

This creates `trace-map.json`.

Inspect it. You should find mappings similar to:

```text
test_checkout
  -> order_service/config.yaml : inventory.timeout
  -> order_service/config.yaml : inventory.retry.attempts

test_inventory_retry
  -> order_service/config.yaml : inventory.retry.attempts

test_pricing_timeout
  -> pricing_service/config.yaml : timeout
```

## 10. Third test: initialize Git

The analyzer compares two Git revisions. For a new copy of the project:

```bash
git init
git config user.name "Your Name"
git config user.email "you@example.com"
git add .
git commit -m "Initial project"
```

## 11. Fourth test: source-code change

Change `sample_microservices/order_service/app.py` from:

```python
return "checkout inventory"
```

to:

```python
return "checkout inventory retry"
```

Commit it:

```bash
git add .
git commit -m "Change checkout behavior"
```

Run:

```bash
python -m analyzer.cli --repo . --tests tests --base HEAD~1 --target HEAD --trace-map trace-map.json --output tia-report.json
```

Inspect `source_changes`, `changed_terms`, and `selected_tests` in `tia-report.json`.

## 12. Fifth test: configuration modification

Change this setting in `sample_microservices/order_service/config.yaml`:

```yaml
attempts: 2
```

to:

```yaml
attempts: 5
```

Commit it:

```bash
git add .
git commit -m "Change inventory retry configuration"
```

Run:

```bash
python -m analyzer.cli --repo . --tests tests --base HEAD~1 --target HEAD --trace-map trace-map.json --output tia-report.json
```

The report should identify:

```text
inventory.retry.attempts
old = 2
new = 5
type = modified
```

The runtime trace map connects this key to `test_checkout` and `test_inventory_retry`, so both tests should be selected.

## 13. Sixth test: timeout modification

Change:

```yaml
inventory:
  timeout: 3
```

to:

```yaml
inventory:
  timeout: 10
```

Commit and run the analyzer again. `inventory.timeout` should be detected and `test_checkout` should be selected by the runtime mapping.

## 14. Seventh test: configuration addition

Add:

```yaml
express_checkout: false
```

under `feature` in the order-service configuration. Commit and run the analyzer. The report should contain `feature.express_checkout` with type `added`.

## 15. Eighth test: configuration removal

Remove:

```yaml
refresh_seconds: 30
```

from the pricing configuration. Commit and run the analyzer. The report should contain `cache.refresh_seconds` with type `removed`.

## 16. Ninth test: run the selected tests

Print selected test paths:

```bash
python -c "import json; print([x['test'] for x in json.load(open('tia-report.json', encoding='utf-8'))['selected_tests']])"
```

Run the printed paths with Pytest.

## 17. Tenth test: complete local workflow

Run:

```bash
pytest -q
python sample_microservices/run_traced_tests.py
python -m analyzer.cli --repo . --tests tests --base HEAD~1 --target HEAD --trace-map trace-map.json --output tia-report.json
```

Then run the selected tests from the report.

## 18. Thesis evaluation

Compare two runs:

### Full test suite

```bash
pytest -q
```

Record:

- Total test count.
- Total execution time.

### Selected test suite

Run the analyzer, count the selected tests, and run only those tests.

Record:

- Selected test count.
- Selected execution time.

Calculate:

```text
Time saved = Full suite time - Selected suite time

Percentage saved = (Time saved / Full suite time) × 100
```

Repeat this with several source-code and configuration changes.

## 19. Important research limitation

This is a working research prototype, not a universal plug-and-play tool for every microservice framework.

For a real application, the configuration-loading/access code must be instrumented so the analyzer can observe the exact setting used at runtime.

The main research demonstration is:

```text
Configuration Change
        |
        v
Exact Changed Key
        |
        v
Runtime Trace
        |
        v
Tests That Used The Key
        |
        v
Selected Tests
```
