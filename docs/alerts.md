# Alert and Runbook

Each alert is symptom-based or SLO-based. Do not alert only on internal implementation names.

## Alert 1

- Name: high_latency_p95
- Severity: warning
- Related SLI/SLO: latency_p95_ms <= 3000
- Condition and duration: p95 latency > 3000 ms for 5 minutes
- User impact: answers are slow and demo requests may time out when concurrency increases
- First checks: inspect latency panel; open the slowest trace; compare logs by correlation_id
- Temporary mitigation: reduce load-test concurrency, disable active incident, rollback the prompt label if a new prompt increased token count
- Owner: observability-oncall

## Alert 2

- Name: elevated_error_rate
- Severity: critical
- Related SLI/SLO: error_rate_pct <= 2
- Condition and duration: error rate > 2% for 5 minutes
- User impact: requests fail or return HTTP 500
- First checks: inspect errors panel; group logs by error_type; open the newest failing trace/correlation_id
- Temporary mitigation: disable active incident, rollback recent config, limit experiment traffic
- Owner: api-oncall

## Alert 3

- Name: low_quality_score
- Severity: warning
- Related SLI/SLO: quality_score_avg >= 0.75
- Condition and duration: quality_score_avg < 0.75 for 10 minutes
- User impact: answers may miss context, be too short, or not address the question
- First checks: inspect quality panel; check prompt_version and prompt_label in traces; read scrubbed message_preview and answer_preview logs
- Temporary mitigation: rollback prompt label to production, check RAG data, pause the candidate prompt
- Owner: ai-quality-oncall
