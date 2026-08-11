# Báo cáo Day 13 Observability

## 1. Thông tin nhóm

- Tên nhóm: Nguyễn Minh Dương - bài cá nhân
- Repository URL: https://github.com/Monmon39/K4-DAY13-2A202601206-NguyenMinhDuong
- Commit SHA cuối: `c11fb5e`
- Thành viên và vai trò:
  - Nguyễn Minh Dương: Logging & PII, tracing/prompt metadata, dashboard/SLO/alerts, incident investigation, report & evidence

## 2. Kết quả kỹ thuật

- Điểm `validate_logs.py`: 100/100
- Tổng số log records đã phân tích: 206
- Số correlation ID duy nhất: 97
- Số PII leak còn lại: 0
- Kết quả `validate_dashboard.py`: hợp lệ, đủ 6/6 panel
- Link/đường dẫn dashboard:
  - Dashboard runtime: `submission/evidence/dashboard-runtime.html`
  - Ảnh dashboard runtime: `submission/evidence/06-dashboard-runtime.jpg`
  - Contract dashboard: `config/dashboard.yaml`
- Môi trường chạy: `APP_ENV=dev`, `APP_NAME=day13-observability-lab`
- Langfuse Cloud: đã cấu hình qua `.env`; `.env` được ignore và không đưa key vào Git/report

## 3. Logging và tracing

- Evidence correlation ID:
  - Log request/response có correlation ID như `req-49a50f59`, `req-70a937e2`, `req-9945440f`.
  - Middleware trả header `x-request-id` và `x-response-time-ms` cho mỗi response.
  - Evidence: `submission/evidence/01-validate-logs.jpg`, `submission/evidence/LOGGING_PII_EVIDENCE.md`
- Evidence PII redaction:
  - Email mẫu được ghi log thành `[REDACTED_EMAIL]`.
  - Số điện thoại Việt Nam mẫu được ghi log thành `[REDACTED_PHONE_VN]`.
  - Số thẻ test được ghi log thành `[REDACTED_CREDIT_CARD]`.
  - Validator báo `Potential PII leaks detected: 0`.
- Evidence trace waterfall:
  - Trace baseline dùng prompt version 1: `submission/evidence/03-langfuse-trace-baseline.jpg`
  - Trace candidate dùng prompt version 2: `submission/evidence/04-langfuse-trace-candidate.jpg`
- Giải thích một span đáng chú ý:
  - Với challenge `rag_slow`, request `req-13de913c` có `latency_ms=2652`, vượt ngưỡng 2000 ms. Đây là tín hiệu khoanh vùng sang bước retrieval/RAG bị chậm.

## 4. Prompt versioning

- Prompt name: `day13-chat`
- Version/label baseline: version 1, label `production`
- Version/label candidate: version 2, từng được promote lên `production` để tạo trace candidate
- Trace ID của mỗi version:
  - Baseline/production v1: `0770a4428f91c1ca038fde50a162fb5e`
  - Candidate v2: `f5d41599c306efd62643b141cd98f64c`
- Trace/evidence của mỗi version:
  - Baseline/production v1: `submission/evidence/03-langfuse-trace-baseline.jpg`
  - Candidate v2: `submission/evidence/04-langfuse-trace-candidate.jpg`
- Bằng chứng đổi label hoặc rollback:
  - Promote version 2 lên production: `submission/evidence/05-langfuse-prompt-promote-v2.png.jpg`
  - Rollback production về version 1: `submission/evidence/05b-langfuse-prompt-rollback-to-v1.png.jpg`
- Ghi chú triển khai:
  - App lấy prompt theo `LANGFUSE_PROMPT_NAME` và `LANGFUSE_PROMPT_LABEL`.
  - Nếu Langfuse không khả dụng, app dùng local fallback `local-v1` và ghi rõ `prompt_source=local` hoặc `local-fallback`.

## 5. Dashboard, SLO và alerts

- Kết quả `validate_dashboard.py`: `HỢP LỆ: 6/6 panel có trong dashboard contract.`
- Evidence dashboard:
  - Validator: `submission/evidence/02-validate-dashboard.jpg`
  - Runtime dashboard: `submission/evidence/06-dashboard-runtime.jpg`
  - HTML dashboard: `submission/evidence/dashboard-runtime.html`
  - Contract: `config/dashboard.yaml`
- Dashboard runtime hiển thị đủ 6 nhóm:
  - Latency percentiles
  - Request traffic
  - Error rate and breakdown
  - Cost over time
  - Input and output tokens
  - Quality proxy
- SLO đã chọn và lý do:
  - `latency_p95_ms <= 3000`: bảo vệ trải nghiệm phản hồi của người dùng.
  - `error_rate_pct <= 2`: phát hiện lỗi API tăng bất thường.
  - `daily_cost_usd <= 2.5`: kiểm soát chi phí thử nghiệm.
  - `quality_score_avg >= 0.75`: theo dõi proxy chất lượng câu trả lời.
- Alert rules và runbook:
  - `high_latency_p95`: warning khi p95 latency > 3000 ms trong 5 phút.
  - `elevated_error_rate`: critical khi error rate > 2% trong 5 phút.
  - `low_quality_score`: warning khi quality score trung bình < 0.75 trong 10 phút.
  - Runbook chi tiết nằm trong `docs/alerts.md`.

## 6. Điều tra challenge

- Challenge ID: `day13-k4-observability-v1`
- Incident: `rag_slow`
- Affected feature: `monitoring`
- Triệu chứng từ metrics/logs:
  - Latency baseline local khoảng 150 ms.
  - Khi bật challenge, các request `monitoring` tăng lên khoảng 2650 ms, vượt ngưỡng 2000 ms.
- Trace/evidence liên quan:
  - Trace baseline/production v1: `0770a4428f91c1ca038fde50a162fb5e`
  - Trace candidate v2: `f5d41599c306efd62643b141cd98f64c`
  - `submission/evidence/CHALLENGE_INVESTIGATION.md`
- Log line/correlation ID liên quan:
  - `req-13de913c`: 2652 ms
  - `req-156852a1`: 2651 ms
  - `req-a28c0a61`: 2651 ms
  - `req-7971c878`: 2650 ms
  - `req-a68b6e88`: 2651 ms
- Root cause:
  - Incident `rag_slow` làm bước RAG retrieval bị delay khoảng 2.5 giây trước khi gọi fake LLM.
- Fix action:
  - Tắt incident `rag_slow`, sau đó kiểm tra/tối ưu retrieval path trước khi bật lại.
- Preventive measure:
  - Theo dõi alert latency p95, mở trace chậm nhất, đối chiếu log bằng correlation ID, và luôn giữ PII redaction trước khi ghi log.

## 7. Đóng góp cá nhân

| Thành viên | Phần việc | Commit/PR | Điều đã học |
|---|---|---|---|
| Nguyễn Minh Dương | Hoàn thiện correlation ID middleware, JSON log enrichment, PII redaction, tracing metadata, prompt fallback, dashboard contract, alert rules, runbook, challenge report và evidence | Repository nộp bài: https://github.com/Monmon39/K4-DAY13-2A202601206-NguyenMinhDuong | Hiểu cách nối Metrics -> Traces -> Logs để chứng minh root cause và cách bảo vệ log khỏi PII |

## 8. Checklist evidence nộp kèm

- `submission/evidence/01-validate-logs.jpg`: kết quả validator log.
- `submission/evidence/02-validate-dashboard.jpg`: kết quả validator dashboard.
- `submission/evidence/03-langfuse-trace-baseline.jpg`: trace prompt version 1.
- `submission/evidence/04-langfuse-trace-candidate.jpg`: trace prompt version 2.
- `submission/evidence/05-langfuse-prompt-promote-v2.png.jpg`: thao tác promote version 2.
- `submission/evidence/05b-langfuse-prompt-rollback-to-v1.png.jpg`: thao tác rollback về version 1.
- `submission/evidence/06-dashboard-runtime.jpg`: dashboard runtime.
