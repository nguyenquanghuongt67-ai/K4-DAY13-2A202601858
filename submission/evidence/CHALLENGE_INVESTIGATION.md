# Challenge Investigation Evidence

- Challenge ID: `day13-k4-observability-v1`
- Incident: `rag_slow`
- Affected feature: `monitoring`
- Latency threshold: `2000ms`

Challenge requests:

| Correlation ID | Feature | Latency |
|---|---|---:|
| `req-13de913c` | monitoring | 2652 ms |
| `req-156852a1` | monitoring | 2651 ms |
| `req-a28c0a61` | monitoring | 2651 ms |
| `req-7971c878` | monitoring | 2650 ms |
| `req-a68b6e88` | monitoring | 2651 ms |

Root cause:

The `rag_slow` incident delays the RAG retrieval path by about 2.5 seconds. The symptom is visible in response logs as latency around 2650 ms, compared with the normal local baseline around 150 ms.

Fix:

Disable `rag_slow`, then inspect and optimize the retrieval step before enabling the feature again.
