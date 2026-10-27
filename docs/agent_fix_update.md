# Cập nhật sửa lỗi Agent — 27/10/2026

## Câu trích cho câu hỏi Part 3

Model đọc được toàn bộ câu trả lời nhưng chỉ được chọn anchor từ các đoạn đã
lưu trong `candidate_points`. Một câu có thật trong transcript vẫn có thể nằm
ngoài các đoạn này. Trước bản sửa, lỗi validation chỉ yêu cầu chọn lại một ý đã
lưu; model có thể lặp lại lựa chọn không hợp lệ đến hết hai lần repair.

Bản sửa gửi kèm các candidate points gần nhất và yêu cầu chọn chuỗi nguyên văn
cùng `turn_id` tương ứng. Không nới lỏng kiểm tra nguồn trích, không tự tạo câu
hỏi thay model, không thay đổi giới hạn hai lần repair hoặc mười model calls.

`tests/test_agent_validation.py` mô phỏng model chọn một câu trong transcript
nhưng ngoài candidate points, rồi chọn lại được khi nhận danh sách hợp lệ.
Test thất bại trước bản sửa và đạt sau bản sửa. Model scripted trong test chỉ
kiểm tra giao thức; không đánh giá chất lượng của model thật.

## SSH tunnel

Script `scripts/start-tunnel.ps1` chờ chính tiến trình SSH mở cổng SOCKS trước
khi báo sẵn sàng. Có giới hạn thời gian kết nối và chờ cổng; nếu không sẵn sàng,
script báo lỗi thay vì chỉ kiểm tra tiến trình sau hai giây.

## Kiểm chứng

- Ruff, kiểm tra cú pháp Python và PowerShell: đạt.
- pytest: 29/29, gồm test regression mới.
- Eval offline: 16/16, dùng model scripted minh bạch.
- Một phiên Gemma `gemma-4-26b` thật hoàn thành 9 câu trả lời, 4 follow-up Part 3
  và assessment; vị trí dẫn chứng hợp lệ, Pronunciation là `not_assessed`.

Lần smoke live dùng câu trả lời giả lập và tăng đồng hồ chuẩn bị 61 giây trong
script; không phải phép kiểm tra thời gian chờ thực tế trên UI. Lần chạy thành
công dùng đúng code Agent của bản sửa này, ghép với Bank, Storage và bộ đề local
hiện có; không phải kết quả CI hay benchmark độ chính xác chấm band.

Trên mạng dùng khi kiểm tra, UIT API xác thực trực tiếp trả HTTP 200. Lần smoke
live bỏ proxy riêng trong tiến trình, không sửa file `.env`. Khi mạng khác cần
SSH, mở tunnel trước và cấu hình `UIT_PROXY` theo README. Không đưa API key,
database, PDF/chunks hoặc nội dung phiên runtime vào Git.

Các số liệu live 10/10 ở báo cáo v2.1 là kết quả lịch sử; smoke live 1/1 ở đây
là lần kiểm tra bổ sung sau bản sửa. Chưa có nhãn band được giám khảo xác nhận,
nên các kiểm tra này không chứng minh độ chính xác của điểm IELTS ước lượng.
