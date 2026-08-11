# Official challenge evidence

- Challenge: `day13-k4-observability-v1`
- Incident: `rag_slow`
- Affected feature: `monitoring`
- Threshold: `latency_threshold_ms=2000`
- Incident enable log: correlation ID `req-0faaee0c`
- Incident disable log: correlation ID `req-a2c2a5e3`

## Metrics symptom

The five official requests returned approximately 2651ms application latency,
above the 2000ms challenge threshold. The normal fake-LLM path is about 150ms
when the slow incident is disabled.

## Trace/log localization

The official request correlation IDs were:

| Session | Correlation ID | Latency |
|---|---|---:|
| k4-challenge-s01 | `req-adacf3cb` | 2650ms |
| k4-challenge-s02 | `req-7eab4321` | 2651ms |
| k4-challenge-s03 | `req-65afb734` | 2651ms |
| k4-challenge-s04 | `req-c1af16d9` | 2651ms |
| k4-challenge-s05 | `req-fc519dac` | 2651ms |

## Root cause

`app/mock_rag.py` intentionally sleeps 2.5 seconds when the `rag_slow`
incident flag is enabled. The extra delay appears before the fake LLM call,
so all five requests cross the threshold while still returning HTTP 200.

## Fix and prevention

- Fix action: disable the incident and verify the same API path returns to the
  normal latency range; the disable event is retained in the logs.
- Preventive measure: alert on p95 latency, open the slow trace, then correlate
  its request ID with the API log before changing the model or prompt.
