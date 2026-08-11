# Alert và Runbook

Mỗi alert phải dựa trên triệu chứng người dùng hoặc SLO, không dựa trực tiếp vào tên implementation nội bộ.

## Alert 1

- Tên: `ai_api_latency_breach`
- Severity: warning
- SLI/SLO liên quan: `latency_p95_ms`, mục tiêu 3000ms
- Điều kiện và thời gian duy trì: p95 > 3000ms trong 10 phút
- Ảnh hưởng tới người dùng: phản hồi chậm hoặc timeout ở tail latency
- Ba bước kiểm tra đầu tiên: xem dashboard latency; mở trace chậm nhất; đối chiếu log theo correlation ID
- Mitigation tạm thời: giảm concurrency, tắt incident/tool chậm nếu đang bật, giữ lại trace và log
- Owner: platform-oncall

## Alert 2

- Tên: `ai_api_error_rate_breach`
- Severity: critical
- SLI/SLO liên quan: `error_rate_pct`, mục tiêu 2%
- Điều kiện và thời gian duy trì: error rate > 2% trong 5 phút
- Ảnh hưởng tới người dùng: request thất bại hoặc không nhận được câu trả lời
- Ba bước kiểm tra đầu tiên: xem error panel; lọc `request_failed`; kiểm tra dependency và rollout gần nhất
- Mitigation tạm thời: rollback thay đổi gần nhất hoặc chuyển sang fallback; thông báo platform-oncall
- Owner: platform-oncall

## Alert 3

- Tên: `ai_api_quality_or_cost_breach`
- Severity: warning
- SLI/SLO liên quan: quality >= 0.75 và daily cost <= 2.5 USD
- Điều kiện và thời gian duy trì: quality < 0.75 hoặc cost > 2.5 USD trong một cửa sổ đánh giá
- Ảnh hưởng tới người dùng: câu trả lời kém hữu ích hoặc chi phí vận hành tăng
- Ba bước kiểm tra đầu tiên: kiểm tra prompt label/version; xem token/cost theo model; lấy mẫu response và quality proxy
- Mitigation tạm thời: rollback prompt label, giới hạn output tokens, chuyển traffic sang prompt/model ổn định
- Owner: ai-platform
