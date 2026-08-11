# Validation Results

## Log Validator

Command:

```bash
.venv/Scripts/python.exe scripts/validate_logs.py
```

Result:

```text
Total log records analyzed: 55
Records with missing required fields: 0
Records with missing enrichment (context): 0
Unique correlation IDs found: 27
Potential PII leaks detected: 0
Estimated Score: 100/100
```

## Dashboard Validator

Command:

```bash
.venv/Scripts/python.exe scripts/validate_dashboard.py
```

Result:

```text
HOP LE: 6/6 panel co trong dashboard contract.
```
