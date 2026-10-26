# Kế hoạch Phase 1 ngày 27 tháng 10 năm 2026

Phạm vi đã chọn: Streamlit + Python/LangGraph, UC03 Speaking bằng text, chạy local.
Repo gốc của lớp đã clone về máy; chưa push. CI chỉ được chuẩn bị và kiểm tra
local; GitHub Actions chưa chạy cho đến khi nhóm tự quyết định push.

## Luồng demo

1. Chọn bộ đề nháp mới được người dùng cho phép dùng thử, bắt đầu với người học giả lập.
2. Part 1 có 4 câu hỏi, mỗi lần trả lời lưu SQLite.
3. Part 2 hiện cue card 4 gợi ý và đếm 60 giây chuẩn bị ở server.
4. Trả lời dài, rồi Part 3 có 4 câu hỏi do model tạo theo hướng trong bank và
   nội dung người học. Anchor phải có trong candidate_points; câu quá giống hoặc
   bị model reviewer đánh giá là trùng nghĩa được yêu cầu sửa. Câu trả lời cực
   ngắn dùng câu hỏi gợi mở <=28 từ, không suy ra band ở từng lượt.
5. Agent đọc skill, truy xuất Speaking descriptors theo tiêu chí và band,
   chấm 3 tiêu chí có thể quan sát từ text, trích dẫn nguyên văn có vị trí.
6. Tool tính band tổng từ 3 tiêu chí. Pronunciation không chấm.
7. UI hiển thị kết quả, nguồn descriptors, giới hạn và tiến trình agent.

## Kiến trúc

Streamlit → SpeakingService → LangGraph model → tool → model → validated final.
SQLite giữ state; JSONL giữ trace theo run ID. UIT adapter gọi Gemma qua SOCKS
SSH nếu ngoài mạng UIT. Model chọn tool và tham số bằng JSON text; không phụ
thuộc native tool calling của server. Output sai được yêu cầu sửa tối đa 2 lần;
agent tối đa 10 lần gọi model mỗi tác vụ.

Tools: load_skill, bank_get_item, retrieve_descriptors, compute_band,
save_attempt (SQLite). `save_attempt` do service gọi sau validation; model không
được ghi tùy ý. Skill: `skills/speaking-examiner/SKILL.md` có contract đầy đủ.
Database là công cụ ngoài thực sự theo mục 4.1 tài liệu đề bài.

## Điều kiện nghiệm thu Phase 1

- Codebase ứng dụng và agent tách thư mục, lệnh cài/chạy tái lập được, có lockfile.
- Một UC chạy từ UI đến model thật và tools; không thay model lỗi bằng điểm giả.
- Agent loop có giới hạn, có tối thiểu 2 tools và 1 skill thực sự được dùng.
- Trace ghi node, tool, skill, chunk ID, token, độ trễ, lỗi; giá chưa biết là null.
- >=10 eval case chạy một lệnh, kết quả JSON; CI dùng model scripted minh bạch.
- Có demo trace và kiểm tra live độc lập; không push trong lượt làm việc này.

## Tách khỏi yêu cầu toàn đồ án

Tập UC 01,02,03,06,07,09,10 phủ K1–K8. Phase 1 chỉ triển khai UC03.
Chưa xây placement, Writing, SRS, hội đồng chấm, full mock test hay teacher dashboard.
UC03 text không chứng minh khả năng phát âm hoặc fluency âm thanh.
Eval luồng/harness không thay thế benchmark Speaking >=10 transcript có nhãn
đã được con người xác nhận; chưa được công bố MAE hoặc đạt ngưỡng ±1 band.
Hai lần regression và các yêu cầu bank/benchmark toàn đồ án là việc giai đoạn sau.

## Mốc thực hiện

1. Kết nối API, tải và chunk descriptors → health check và đủ metadata.
2. State, tools, skill, loop → test transition, repair, permissions và dẫn chứng.
3. Streamlit → đi hết phiên và xem trace/kết quả.
4. Eval, CI, demo guide → chạy local; ghi rõ kết quả thật và phần chưa xác minh.
