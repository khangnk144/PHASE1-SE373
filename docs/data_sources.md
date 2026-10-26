# Nguồn dữ liệu và giấy phép

## Đề Speaking

`data/bank/speaking.json` là 10 bộ người dùng cung cấp trong
`DoAn/speaking_bank_draft`, được import cho demo local theo yêu cầu trực tiếp.
Giữ `source=llm_generated`, `verification.status=pending_human_review`, người
duyệt và thời điểm duyệt để null. Đây không phải bank đã được nhóm xác nhận.
`ALLOW_DRAFT_BANK=1` cho phép dùng thử; giá trị 0 chặn tạo phiên từ draft.

Phần câu hỏi mới dự kiến CC BY 4.0; không áp dụng giấy phép này lên tài liệu
tham khảo. Danh sách nguồn và tự rà soát do người dùng cung cấp được giữ ở
[docs/bank/speaking_sources.md](bank/speaking_sources.md) và
[docs/bank/speaking_review.md](bank/speaking_review.md). Đã sửa một lỗi logic ở
sp-technology: hỏi vì sao thay đồ bị hỏng thay vì sửa, thay cho “working items”.
File gốc bên ngoài repo được giữ nguyên. Nhóm vẫn cần tự xác nhận nội dung.

Bank ban đầu và dữ liệu phiên trước đã xoá theo yêu cầu; không có fallback sang
đề cũ. Mỗi phiên lưu snapshot/hash riêng. Chỉ chuyển nguồn sang
llm_generated_verified khi có status=approved, người duyệt và thời điểm duyệt
được ghi thực tế; loader không tự tạo thông tin xác nhận.

## Speaking descriptors chính thức

Nguồn: [IELTS Speaking Band Descriptors](https://ielts.org/cdn/ielts-guides/ielts-speaking-band-descriptors.pdf).
Tài liệu bản quyền của chủ sở hữu IELTS, không gán CC BY cho tài liệu này.
Repo chỉ có URL và script tải; PDF và toàn bộ chunks ở `runtime/knowledge/`,
bị Git ignore. Không đưa PDF/chunks vào sample trace hay phân phối lại trong repo.
Nhóm cần đọc điều kiện sử dụng của nguồn trước khi công khai hoặc mở rộng.

Ingestion ghi SHA-256 của PDF, ngày tải và version theo hash. Chunk theo từng
criterion × band; metadata gồm test_part, criterion, band, version, source_url
và page. Kiểm tra đủ 27 chunks cho ba tiêu chí text, band 1–9. PDF hiện tải
được 36 chunks gồm cả Pronunciation; tool assessment text chỉ cho truy xuất ba
tiêu chí được chấm. Retrieval là metadata/rule-based, không giả nhận là vector RAG.

## Eval và người học

Toàn bộ câu trả lời ở `evals/fixtures.py` và `scripts/smoke_live.py` là giả lập.
Không dùng thông tin hoặc bài làm của người thật. Fixture descriptors trong
eval offline là chuỗi test do dự án tự tạo, gắn `TEST_ONLY`, không phải rubric
chính thức. Live eval dùng descriptors tải thật và model thật.

Chưa có benchmark band được xác nhận. Trước khi đánh giá độ chính xác UC03
toàn đồ án, nhóm cần ít nhất 10 transcript và mỗi nhãn cần: source/license,
phương pháp gán nhãn, nhãn gợi ý nếu có, nhãn cuối, người kiểm và thời điểm xác
nhận. Người kiểm đối chiếu cả ba tiêu chí text với descriptors, điều chỉnh nhãn
gợi ý, rồi ký xác nhận. Không được tự điền người kiểm hoặc đánh dấu xác nhận
thay cho thành viên nhóm. Report hiện để `band_accuracy=null`.

## API và tài liệu kỹ thuật

- [UIT LLM](https://llm.uit.edu.vn/) — model API của nhóm, credential chỉ trong .env.
- Lab nội bộ `Buoi3/BTVN3/lib/model_that.py` và `Buoi4/BTVN4/uit-tool-call-proxy.py`
  được đọc để hiểu `tool_choice=none`, parsing và SSH; code đồ án dùng JSON action
  protocol riêng, không phụ thuộc đường dẫn lab khi chạy trên máy khác.
- [LangGraph Graph API](https://docs.langchain.com/oss/python/langgraph/graph-api)
  — model/tool cycle và conditional edges.
- [uv](https://docs.astral.sh/uv/) — môi trường và lockfile.
