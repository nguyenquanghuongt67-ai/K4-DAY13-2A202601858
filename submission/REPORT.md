# Báo cáo Day 13 Observability

## 1. Thông tin nhóm

- Tên nhóm: K4-Day13-2A202601858
- Repository URL: https://github.com/nguyenquanghuongt67-ai/K4-DAY13-2A202601858.git
- Commit SHA cuối: điền sau khi commit
- Thành viên và vai trò:
  + Nguyễn Quang Hướng: Logging & Middleware

## 2. Kết quả kỹ thuật

- Điểm `validate_logs.py`: 100/100; 0 PII leak; 0 record thiếu field/enrichment
- Tổng số traces: 11 traces thuộc lần chạy này truy vấn được từ Langfuse Cloud; 10 dùng prompt version 2 và 1 rollback dùng version 1
- Số PII leak còn lại: 0 theo validator độc lập
- Link/đường dẫn dashboard: http://localhost:8501

## 3. Logging và tracing

- Evidence correlation ID: `submission/evidence/correlation_id_and_pii.md`
- Evidence PII redaction: `submission/evidence/correlation_id_and_pii.md`
- Evidence trace waterfall: trace `82a646a95a436091cbcd2cd4f9f65c8d` trên Langfuse
- Giải thích một span đáng chú ý: challenge chậm nằm ở bước RAG khi `rag_slow` bật; trace có metadata prompt và generation usage/cost

## 4. Prompt versioning

- Prompt name: `day13-chat`
- Version/label baseline: v1 / `production` trong rollback kiểm chứng
- Version/label candidate: v2 / `production` sau khi restore
- Trace ID của mỗi version: v1 `8f3beac64e659b639ffd8ce232e040c7`; v2 `82a646a95a436091cbcd2cd4f9f65c8d`
- Bằng chứng đổi label hoặc rollback: `submission/evidence/prompt_version_status.md`; production đã restore về v2

## 5. Dashboard, SLO và alerts

- Kết quả `validate_dashboard.py`: `HỢP LỆ: 6/6 panel`
- Evidence dashboard: `submission/evidence/dashboard_validation.txt`; dashboard code ở `scripts/dashboard.py` và `scripts/streamlit_app.py`
- SLO đã chọn và lý do: p95 latency <= 3000ms, error rate <= 2%, daily cost <= 2.5 USD, quality >= 0.75
- Alert rules và runbook: `config/alert_rules.yaml`, `config/slo.yaml`, `docs/alerts.md`

## 6. Điều tra challenge

- Challenge ID: `day13-k4-observability-v1`
- Triệu chứng từ metrics: 5/5 official requests có application latency tăng vọt lên mức 11,000ms - 14,000ms, vượt xa ngưỡng 3000ms (hiển thị màu đỏ BREACH trên Dashboard).
- Trace ID liên quan: Langfuse trace ghi nhận span `retrieve` (RAG) bị chậm bất thường.
- Log line/correlation ID liên quan: `req-fa9b9025`, `req-1e39a66f`, `req-71c8b3be`, `req-a54fe634`, `req-7c4e748c`
- Root cause: `app/mock_rag.py` sleep 2.5 giây khi incident `rag_slow` bật
- Fix action: disable incident; xác nhận request sau đó trở về khoảng 150ms
- Preventive measure: alert p95, mở trace chậm, rồi đối chiếu correlation ID với log trước khi sửa model/prompt

## 7. Đóng góp cá nhân

Với mỗi thành viên, ghi rõ nhiệm vụ và link commit/PR tương ứng.

| Thành viên | Phần việc | Commit/PR | Điều đã học |
|---|---|---|---|
| Nguyễn Quang Hướng | **(Logging & Middleware):** Phụ trách CP1 (Middleware, Correlation ID, gán log metadata). | ae865c40845d14665b20d8cdcc51ae2f4b06424f | Hiểu cách luân chuyển request ID và làm giàu metadata trong hệ thống. | 
| Nguyễn Minh Dương | **(Security & Compliance):** Phụ trách CP1 (Uncomment processor, cấu hình regex patterns che PII toàn cục). | *(Chung nhánh Huy)* | Biết cách thiết lập bộ lọc sanitize tránh rò rỉ dữ liệu nhạy cảm (email, phone, thẻ). |
| Đinh Xuân Hiệp | **(Metrics & Alerting):** Phụ trách CP2 (Tích hợp Langfuse, đo error_rate_pct, SLO, Alert rules, Runbook). | *(Chung nhánh Huy)* | Nắm được nguyên lý SDK Langfuse gửi trace và cách thiết lập cảnh báo chuẩn xác. |
| Võ Quốc Huy | **(QA & Incident Analyst):** Chạy load test, thiết kế Dashboard, điều tra Challenge (CP3) & báo cáo. | *(Chung nhánh Huy)* | Nắm trọn vẹn workflow phân tích sự cố: từ Dashboard (Metrics) -> Langfuse (Traces) -> Logs. |
