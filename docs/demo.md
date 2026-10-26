# Kịch bản demo Phase 1

1. Chạy tunnel, kiểm tra descriptors, rồi `uv run streamlit run app/main.py`.
2. Chọn Quiet Spaces và bắt đầu. Chỉ dùng nhân vật giả lập. Nêu rõ bộ mới là
   bản nháp người dùng cho phép thử trước, chưa được nhóm rà soát chính thức.
3. Trả lời Part 1 bằng tiếng Anh, ví dụ các câu trong `scripts/smoke_live.py`.
4. Part 2: chỉ ra cue card 4 gợi ý, timer 60 giây. Bấm bắt đầu sớm sẽ được
   nhắc tiếp tục chuẩn bị; server chỉ chuyển phần sau khi đủ thời gian.
5. Nhập câu trả lời dài. Mở tab Tiến trình agent để chỉ ra model → load_skill
   → model → câu hỏi Part 3 có anchor từ câu trả lời trước.
   Trace adaptive_question_plan ghi hướng/cách hỏi; semantic_question_review
   ghi quyết định trùng nghĩa. Không đọc hết bốn câu trong pool như kịch bản cố định.
6. Trả lời 4 câu Part 3. Chỉ ra retrieve_descriptors, compute_band và save_attempt.
7. Xem nhận xét theo từng tiêu chí, quote và vị trí transcript, refs có nguồn.
   Chỉ ra Pronunciation not_assessed, giới hạn text và nhãn điểm ước lượng.
8. Tải kết quả JSON. Không gọi band này là điểm chuẩn hoặc điểm thi thật.
9. Chạy `uv run python -m evals.run --all`; giải thích đây là 16 case harness
   offline, không phải 16 bài được model chấm đúng.
10. Mở kết quả `runtime/evals/live-report.json` và trace tương ứng nếu đã chạy
    live eval. Trình bày đúng số đạt/thất bại trong report, không bỏ case fail.

Nếu API không đáp ứng, giữ nguyên phiên và dùng Thử lại bước agent khi kết nối
khôi phục. Có thể mở phiên đã hoàn tất bằng mã phiên trong SQLite để xem lại
kết quả, nhưng phải nói rõ đó là kết quả đã lưu, không phải một lần chấm live mới.

CI đã cấu hình và kiểm tra các lệnh local. Chưa push nên không trình bày như đã
có GitHub Actions xanh. Không cần chạy `git push` để demo bản local.
