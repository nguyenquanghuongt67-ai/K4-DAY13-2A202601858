# Logging evidence

- Every API request has a `req-<8 hex>` correlation ID in the log and response header.
- The run produced more than two unique correlation IDs and the validator found no missing enrichment.
- `user_id` is represented as a 12-character SHA-256 prefix (`user_id_hash`).
- Request and response previews pass through the independent PII scrubber.
- Validator result: `Potential PII leaks detected: 0` and `Estimated Score: 100/100`.
