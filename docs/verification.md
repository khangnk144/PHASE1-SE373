# Kết quả kiểm tra local ngày 26 tháng 10 năm 2026

Tài liệu này lưu bằng chứng bản v1. Cập nhật bank và adaptive Part 3 bản v2 xem
[bank_v2_update.md](bank_v2_update.md); không dùng số liệu v1 để mô tả code v2.

## Đã chạy và quan sát

- SSH qua baotg@192.168.20.150 thành công; Gemma thật trả HTTP 200.
- Cài độc lập bằng uv, có uv.lock. Lint và compile Python thành công.
- Pytest: 16 passed. Do môi trường chạy giới hạn thư mục tạm trên Windows,
  lệnh kiểm tra local dùng `--basetemp runtime/pytest-final`; CI/Linux dùng
  lệnh pytest chuẩn không cần tham số này.
- Eval offline: 16/16 case harness đạt.
- Eval live: 10/10 phiên giả lập qua Gemma đạt kiểm tra harness; 144 lần gọi
  model, 406777 input tokens, 11398 output tokens. Giá chưa biết, cost_usd=null.
  Đây là số đo của lần chạy lưu kèm, không phải cam kết chi phí hoặc độ trễ cố định.
- Đã thao tác trên trình duyệt từ bắt đầu, nhập 4 câu Part 1, cue card và thời
  gian chuẩn bị thực tế, 1 câu Part 2, 4 câu Part 3 đến kết quả cuối cùng.
- Màn hình kết quả có band ước lượng, dẫn chứng nguyên văn/vị trí, gợi ý luyện
  tập và Pronunciation not_assessed. Tab trace có tiến trình model/tool/skill.
- `.env`, `.venv` và runtime bị Git ignore. Đã quét key thực tế trong toàn bộ
  file có thể được Git đưa vào repo, không thấy key bị lộ. Sample trace không
  chứa câu trả lời nguyên văn.

## Bằng chứng

- [Report offline](evidence/report.json)
- [Report 10 phiên Gemma thật](evidence/live-report.json)
- [Trace một phiên hoàn tất qua UI](evidence/uc03-live.jsonl)

Sample trace chỉ có dữ liệu giả lập, IDs và metadata. Các run ID trong report
live trỏ tới trace đầy đủ lưu local tại runtime/traces; chúng không được tự động
đưa toàn bộ vào Git. Phiên UI trong trace có mã
`14cc83cade6e4ae6b4d0ddb6228e24bb`. Dữ liệu phiên này đã xoá theo yêu cầu reset;
trace là bằng chứng kiểm thử lịch sử, không còn là phiên có thể mở lại trong app.

## Chưa được chứng minh trong Phase 1

Chưa có nhãn benchmark band được con người xác nhận, nên không báo cáo MAE,
QWK hay tỷ lệ chấm lệch <=1 band. Không có tuyên bố rằng điểm ước lượng là
điểm đúng. Kiểm tra lặp bằng văn bản và anchor không thay thế evaluator ngữ
nghĩa độc lập. Chưa triển khai STT/TTS hoặc các UC khác.

CI đã viết và các bước kiểm tra chính đã chạy local. Chưa push, chưa có lần
chạy GitHub Actions cho phần code này. Chưa commit, publish hay deploy.
