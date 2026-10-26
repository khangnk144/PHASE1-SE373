# IELTS Learning Agent

**SE373 · Nhóm 38 · Phase 1**

Ứng dụng luyện IELTS Speaking với AI đóng vai giám khảo, dẫn dắt phiên thi thử
ba phần và đưa ra nhận xét có dẫn chứng từ câu trả lời của người học. Bản Phase 1
triển khai **UC03 — Speaking mock test nhiều phần có câu hỏi đào sâu**, chạy bằng
text trên máy local.

Điểm do hệ thống đưa ra là **ước lượng phục vụ luyện tập**, không thay thế kết
quả thi IELTS chính thức.

## Tính năng

- **Thi thử đủ ba phần:** 4 câu Part 1, cue card Part 2 với 60 giây chuẩn bị,
  một lượt trả lời dài và 4 câu thảo luận Part 3.
- **Câu hỏi theo nội dung trả lời:** Part 3 kết hợp hướng thảo luận trong ngân
  hàng đề với những ý người học đã nói; câu trả lời ngắn được gợi mở ngắn hơn.
- **Chấm có căn cứ:** truy xuất Speaking band descriptors, trích dẫn nguyên văn
  từ transcript và kiểm tra vị trí của từng dẫn chứng.
- **Kiểm soát đầu ra:** schema cho trạng thái và kết quả, tool tính band tổng,
  kiểm tra câu hỏi lặp ý và giới hạn số bước thực thi.
- **Lưu phiên và phục hồi:** SQLite lưu câu trả lời trước khi gọi model; khi API
  lỗi, người học có thể thử lại bước đang chờ mà không nộp lại bài.
- **Quan sát tiến trình:** giao diện hiển thị các bước model, tool và skill;
  JSONL trace ghi run ID, token, độ trễ và thông tin lỗi.

Ngân hàng hiện có **10 bộ đề do AI hỗ trợ biên soạn**, được đánh dấu
`pending_human_review` để nhóm tiếp tục rà soát trước khi xác nhận chất lượng.

## Công nghệ và kiến trúc

| Thành phần | Công nghệ |
|---|---|
| Giao diện | Streamlit |
| Agent workflow | Python, LangGraph |
| Mô hình | Gemma qua UIT LLM API |
| Schema và validation | Pydantic |
| Lưu trữ | SQLite |
| Quản lý môi trường | uv và uv.lock |
| Kiểm tra | pytest, Ruff, GitHub Actions |

```text
Streamlit → SpeakingService → LangGraph → Model ⇄ Tools
                  ↓                         ↓
                SQLite             Validation → Kết quả
                  └──────── JSONL trace ─────┘
```

Agent sử dụng giao thức hành động JSON với `tool_choice="none"` để làm việc với
API UIT. Model chọn tool và tham số; workflow kiểm tra, thực thi và trả kết quả
cho model ở bước kế tiếp. Mỗi tác vụ giới hạn **10 lần gọi model** và tối đa
**2 lần yêu cầu sửa đầu ra**.

| Tool | Vai trò |
|---|---|
| `load_skill` | Đọc hướng dẫn `speaking-examiner` |
| `retrieve_descriptors` | Truy xuất mô tả Speaking theo tiêu chí và band |
| `compute_band` | Tính band tổng bằng code |
| `bank_get_item` | Lấy bộ đề cùng metadata nguồn và giấy phép |
| `save_attempt` | Lưu trạng thái và câu trả lời vào SQLite |

Ba tool đầu do model lựa chọn; hai tool còn lại được service gọi để điều phối
phiên. Skill có contract tại [skills/speaking-examiner/SKILL.md](skills/speaking-examiner/SKILL.md).

RAG tách tài liệu theo **tiêu chí × band**, giữ metadata nguồn, trang và phiên
bản, sau đó truy xuất bằng bộ lọc metadata. PDF và các chunk được tải khi cài
đặt, lưu trong `runtime/knowledge/` và không đưa vào Git.

## Cài đặt và chạy

### Yêu cầu

- Python **3.11–3.14**, khuyến nghị **3.13**.
- Git và [uv](https://docs.astral.sh/uv/).
- API key và quyền truy cập [UIT LLM](https://llm.uit.edu.vn/).
- Kết nối trực tiếp tới API UIT, hoặc SSH tới một máy được cấp quyền trong mạng UIT.

### 1. Tải source và cài dependency

Các lệnh bên dưới dùng PowerShell trên Windows:

```powershell
git clone https://github.com/khangnk144/PHASE1-SE373.git
cd PHASE1-SE373
uv sync --frozen --python 3.13
```

### 2. Cấu hình môi trường

Tạo `.env` nếu chưa có:

```powershell
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
```

Điền `OPENAI_API_KEY` trong `.env`. Các thiết lập chính:

| Biến | Ý nghĩa |
|---|---|
| `OPENAI_API_KEY` | API key UIT của người chạy |
| `OPENAI_BASE_URL` | Mặc định `https://llm.uit.edu.vn/gemma/v1` |
| `MODEL_NAME` | Mặc định `gemma-4-26b` |
| `UIT_PROXY` | Để trống khi truy cập trực tiếp; dùng SOCKS khi qua SSH |
| `ALLOW_DRAFT_BANK` | `1` cho phép dùng bộ đề nháp; `0` chỉ nhận đề đủ điều kiện duyệt |

Xem đầy đủ cấu hình tại [.env.example](.env.example).

Nếu cần kết nối qua máy SSH của nhóm:

```powershell
.\scripts\start-tunnel.ps1
```

Script dùng `baotg@192.168.20.150`, tạo SOCKS tại `127.0.0.1:1081` và yêu cầu
SSH key đã được cấu hình trên máy người chạy. Đây là cấu hình hạ tầng của nhóm;
người dùng khác cần tài khoản và máy SSH được cấp quyền tương ứng.
Đặt `UIT_PROXY=socks5://127.0.0.1:1081` khi dùng tunnel này.

### 3. Chuẩn bị tri thức và mở ứng dụng

```powershell
uv run python scripts/bootstrap_descriptors.py
uv run streamlit run app/main.py
```

Mở **[http://127.0.0.1:8501](http://127.0.0.1:8501)**, chọn chủ đề và bắt đầu
phiên luyện tập. Tab **Tiến trình agent** hiển thị các bước xử lý; kết quả cuối
có thể tải dưới dạng JSON. Script SSH in PID để dừng tunnel khi kết thúc.

## Kiểm thử và đánh giá

### Kiểm tra offline

Không cần API key hoặc kết nối UIT:

```powershell
uv run ruff check .
uv run pytest -q
uv run python -m evals.run --all
```

Bộ offline dùng model scripted để kiểm tra workflow, schema, tools, lưu trữ,
retry và guardrails. Report được ghi vào `runtime/evals/report.json`.

### Đánh giá với model thật

Cần `.env`, kết nối UIT và descriptors đã được chuẩn bị:

```powershell
uv run python scripts/smoke_live.py
uv run python -m evals.live --workers 2
uv run python -m evals.semantic
```

### Kết quả đã ghi nhận

| Bộ kiểm tra | Kết quả local | Bằng chứng |
|---|---:|---|
| pytest | 28/28 | [Báo cáo kiểm chứng](docs/bank_v2_update.md) |
| Eval harness offline | 16/16 | [Report JSON](docs/evidence/bank-v21-offline.json) |
| Phiên giả lập với Gemma thật | 10/10 | [Report JSON](docs/evidence/bank-v21-live.json) |
| Kiểm tra trùng nghĩa trên các cặp câu hỏi | 5/5 | [Report JSON](docs/evidence/semantic-v2.json) |

Các số liệu trên đánh giá **luồng thực thi và các ràng buộc của harness**.
Chúng chưa xác nhận độ chính xác của band so với giám khảo. Đồng hồ chuẩn bị
được tăng tốc trong script eval; ứng dụng vẫn kiểm tra đủ 60 giây.

[GitHub Actions](https://github.com/khangnk144/PHASE1-SE373/actions) được cấu hình
chạy lint, pytest và eval offline, không sử dụng API key. Trạng thái CI của từng
commit được hiển thị trong tab Actions.

## Phạm vi và giới hạn

- Bản hiện tại chỉ triển khai **UC03 ở chế độ text**. Chưa có STT/TTS hoặc chức
  năng chọn luyện riêng từng Part.
- **Pronunciation luôn là `not_assessed`.** Band tổng chỉ tính từ ba tiêu chí
  được đánh giá qua text; không quan sát được tốc độ nói hay ngập ngừng thực tế.
- Cách hỏi thích ứng theo nội dung và độ dài câu trả lời là heuristic, chưa phải
  cơ chế điều chỉnh độ khó theo band được hiệu chuẩn.
- Bước kiểm tra trùng nghĩa dùng model và có thể sai. Ngân hàng đề vẫn chờ nhóm
  rà soát; chưa có benchmark band được con người xác nhận để báo cáo MAE/QWK.

## Dữ liệu và bảo mật

Ứng dụng dành cho người học giả lập trên máy local, chưa có hệ thống tài khoản
và phân quyền cho nhiều người dùng. Câu trả lời được lưu trong SQLite; trace chỉ
chứa metadata, không ghi nguyên văn câu trả lời hoặc prompt model.

`.env`, `.venv/`, database và toàn bộ `runtime/` được Git bỏ qua. Repository chỉ
cung cấp `.env.example` với API key để trống. Các phiên không hoạt động quá
7 ngày được dọn khi khởi tạo kho lưu trữ; người dùng có thể xoá phiên ngay trong giao diện.

## Cấu trúc dự án

```text
app/          Giao diện Streamlit
agent/        Workflow, model adapter, tools, schema và session service
skills/       Hướng dẫn tái sử dụng cho agent
data/bank/    Bộ đề và metadata nguồn
evals/        Eval offline và live
tests/        Kiểm tra tự động
scripts/      Chuẩn bị descriptors, SSH tunnel và smoke test
docs/         Kiến trúc, nguồn dữ liệu và bằng chứng kiểm thử
runtime/      Dữ liệu sinh khi chạy, không được đưa vào Git
```

## Tài liệu

- [Kiến trúc hệ thống](docs/architecture.md)
- [Nguồn dữ liệu và giấy phép](docs/data_sources.md)
- [Kịch bản demo](docs/demo.md)
- [Kết quả cập nhật bank và Part 3](docs/bank_v2_update.md)
- [Minh bạch sử dụng AI](docs/ai_usage.md)
