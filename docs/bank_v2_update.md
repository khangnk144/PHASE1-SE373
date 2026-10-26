# Cập nhật bank và adaptive Part 3 bản v2.1

Đã import 10 bộ đề người dùng cung cấp cho demo local. Source vẫn là
llm_generated, trạng thái pending_human_review, reviewer và reviewed_at là null.
Bộ gốc ở DoAn/speaking_bank_draft được giữ nguyên; bản import sửa câu hỏi
replace working items thành replace broken items. Theo yêu cầu reset tiếp theo,
bank ban đầu và các phiên trước đã xoá. Mỗi phiên lưu snapshot/hash của đề mới.

## Hành vi Part 3

Mỗi lượt lấy một hướng thảo luận và câu tham khảo trong bank. Model chọn một
đoạn từ candidate_points để tạo câu hỏi có liên hệ đến câu trả lời trước.
Câu trả lời <=5 từ dùng nhánh gợi mở, giới hạn câu hỏi <=28 từ kể cả anchor;
6–34 từ dùng câu thảo luận rõ ràng; >=35 từ hướng model đào sâu lý do, hệ quả,
so sánh hoặc đánh đổi. Đây là heuristic chọn cách hỏi, không phải đánh giá
band, hiểu chắc trình độ hay hiệu chuẩn độ khó. Không đọc pool như script cố định.

Anchor một từ như Yes được phép khi đó là toàn bộ câu người học đã nói.
Chỉ căn lại chữ hoa/thường khi tìm được chính chuỗi đó trong câu trả lời; không
fuzzy-match hay bịa lời người học. Với câu trả lời nghèo nội dung, một anchor
đúng văn bản chưa chứng minh đó là ý nghĩa phong phú để đào sâu.

Câu hỏi qua kiểm tra giống chữ và một invocation riêng đánh giá trùng ý.
Reviewer có thể sai; không tuyên bố loại được mọi câu đồng nghĩa. Reviewer
vẫn tính trong giới hạn 10 model calls/tác vụ. Kết quả cuối được xác thực
bằng SpeakingAssessment trước lưu/xuất; Pronunciation luôn not_assessed.

## Kết quả đã chạy

- Lint đạt; pytest 28/28 (16 harness + 12 kiểm tra bank/adaptive/schema).
- Eval runner offline 16/16, dùng model scripted minh bạch.
- Live Gemma: 10/10 phiên hoàn tất và qua các kiểm tra hiện có.
- Kiểm tra semantic riêng: 5/5 cặp gồm paraphrase, quote prefix và các mục đích khác nhau.
- Phiên UI mới hiển thị Quiet Spaces và nhãn đang chờ rà soát, lấy đúng câu hỏi bank mới.
- 190 lần gọi model; 514301 input tokens,
  14615 output tokens; giá chưa biết nên cost_usd=null.
- Trung bình 33.09 giây/case live trên lần chạy này; thời gian chuẩn bị chỉ
  tăng tốc trong script, không phải thời lượng một phiên thi có người thật.

| Bản | Phiên live đạt | Model calls | Input tokens | Output tokens |
|---|---:|---:|---:|---:|
| v1 trước cập nhật | 10/10 | 141 | 393437 | 10676 |
| v2.1 hiện tại | 10/10 | 190 | 514301 | 14615 |

Bank và prompt đều thay đổi; số liệu trên chỉ so sánh luồng/harness và tài nguyên,
không cô lập tác động của một thay đổi và không phải so sánh độ chính xác chấm band.
Các lần thử trung gian đã phát hiện lỗi lấy nhầm examiner quote và khác casing;
đã sửa, thêm kiểm tra hồi quy và giữ log lỗi trong runtime thay vì bỏ qua validation.

Bằng chứng hiện tại:
- [Report offline](evidence/bank-v21-offline.json)
- [Report live](evidence/bank-v21-live.json)
- [Trace một phiên v2.1](evidence/uc03-bank-v21.jsonl)
- [Semantic checks](evidence/semantic-v2.json) — prompt reviewer không thay đổi.

## Phần còn lại

Nhóm cần rà soát bank và ghi người duyệt thực tế. Chưa có benchmark Speaking
với nhãn band được con người xác nhận, nên chưa đo MAE/QWK hoặc ngưỡng sai số
<=1 band ở >=80% transcript. Vẫn chỉ triển khai UC03 text; chưa thêm chọn luyện
riêng từng Part. Report này ghi nhận kiểm tra local trước khi push; xem tab
Actions của repo để biết trạng thái CI trên GitHub.
