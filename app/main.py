import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import streamlit as st
import streamlit.components.v1 as components

from agent.bank import session_item
from agent.config import DISCLAIMER, ROOT, TEXT_LIMITATION, Settings
from agent.graph import AgentError
from agent.provider import ModelError, UITModel
from agent.service import SpeakingService
from agent.storage import Store
from agent.tools import load_bank

st.set_page_config(page_title="Speaking Studio · Nhóm 38", page_icon="🌿", layout="wide")


def event_label(event):
    labels = {
        "run_started": "Bắt đầu xử lý", "node_started": "Bước: " + event.get("node", ""),
        "model_started": "Đang gọi Gemma UIT", "model_completed": "Đã nhận phản hồi model",
        "tool_started": "Gọi tool: " + event.get("tool", ""),
        "tool_completed": "Tool hoàn tất: " + event.get("tool", ""),
        "skill_loaded": "Đã đọc skill speaking-examiner", "schema_repair": "Đang sửa đầu ra theo schema",
        "final_validated": "Đã kiểm tra kết quả", "run_completed": "Đã lưu phiên",
        "guardrail": "Đã áp dụng quy tắc của phiên thi",
        "adaptive_question_plan": "Đang chọn cách hỏi tiếp theo từ nội dung bạn đã trả lời",
        "semantic_question_review": "Đã kiểm tra câu hỏi có lặp ý trước đó không",
    }
    return labels.get(event["event"], event["event"])


def service():
    return SpeakingService(UITModel(Settings.load()))


def render_result(session):
    result = session.assessment
    st.subheader("Nhận xét cho phiên luyện tập")
    st.warning(result["disclaimer"])
    if result.get("bank_provenance", {}).get("verification") == "pending_human_review":
        st.info("Phiên này dùng bộ đề nháp đang chờ nhóm rà soát.")
    st.metric("Band tổng ước lượng từ 3 tiêu chí text", result["overall_band"])
    st.caption(result["limitations"] + " Độ tin cậy: " + result["confidence"] + ".")
    labels = {
        "fluency_coherence": "Fluency & Coherence · quan sát từ text",
        "lexical_resource": "Lexical Resource",
        "grammatical_range_accuracy": "Grammatical Range & Accuracy",
        "pronunciation": "Pronunciation",
    }
    for criterion in result["criteria"]:
        band = criterion["band"]
        title = labels[criterion["criterion"]] + (
            f" · Ước lượng {band}" if band is not None else " · not_assessed"
        )
        with st.expander(title, expanded=True):
            st.write(criterion["comment"])
            for evidence in criterion["evidence"]:
                st.caption(
                    f"Câu trả lời {evidence['turn_id']} · "
                    f"vị trí {evidence['start_char']}–{evidence['end_char']} trong transcript"
                )
                st.text(evidence["quote"])
            if criterion["descriptor_refs"]:
                st.caption("Speaking descriptor refs: " + ", ".join(criterion["descriptor_refs"]))
    st.markdown("**Gợi ý luyện tập tiếp theo**")
    for improvement in result["improvements"]:
        st.write("• " + improvement)
    st.link_button(
        "Xem Speaking band descriptors chính thức",
        "https://ielts.org/cdn/ielts-guides/ielts-speaking-band-descriptors.pdf",
    )
    with st.expander("Transcript của phiên · dùng đối chiếu vị trí dẫn chứng"):
        st.text(result["transcript"])
    st.download_button(
        "Tải kết quả JSON", json.dumps(result, ensure_ascii=False, indent=2),
        file_name="speaking-practice-result.json", mime="application/json",
    )


def render_trace(session):
    rows = []
    for run_id in session.run_ids:
        path = ROOT / "runtime" / "traces" / f"{run_id}.jsonl"
        if path.exists():
            rows.extend(json.loads(line) for line in path.read_text(encoding="utf-8").splitlines())
    st.caption("Trace chỉ có metadata; không ghi nội dung câu trả lời hay prompt model.")
    st.json(rows, expanded=False)


def preparation(session_id, started_at):
    deadline_ms = int((started_at + 60) * 1000)
    components.html(
        f"""<div style="font:16px sans-serif;color:#23372F;padding:10px 0">
        Thời gian chuẩn bị còn lại<br><strong id="clock" style="font-size:32px"></strong>
        <div id="ready" style="margin-top:8px"></div></div>
        <script>
        function tick() {{
            const remaining = Math.max(0, Math.ceil(({deadline_ms} - Date.now()) / 1000));
            document.getElementById('clock').textContent = remaining + ' giây';
            document.getElementById('ready').textContent = remaining === 0
                ? 'Bạn đã có đủ thời gian chuẩn bị. Hãy bắt đầu trả lời.' : '';
        }}
        tick(); setInterval(tick, 250);
        </script>""",
        height=115,
    )
    st.caption("Chuẩn bị ý chính. Khi đủ 1 phút, bắt đầu phần trả lời dài bằng text.")
    if st.button("Bắt đầu trả lời Part 2", type="primary"):
        try:
            service().begin_part2(session_id)
            st.rerun()
        except ValueError as error:
            st.info(str(error))


st.caption("SE373 · NHÓM 38 · PHASE 1")
st.title("Speaking Studio")
st.write("Luyện một phiên Speaking, từng câu một. Nhận góp ý có dẫn chứng từ chính bài của bạn.")
st.caption("Bản demo local dành cho người học giả lập · UC03 · Text mode")

store = Store()
with st.sidebar:
    st.subheader("Phiên luyện tập")
    st.caption("Gemma UIT · LangGraph · SQLite")
    st.info(TEXT_LIMITATION)
    st.caption("Dữ liệu phiên local giữ tối đa 7 ngày. Có thể xoá ngay bằng nút bên dưới.")
    if "session_id" in st.session_state:
        st.code(st.session_state.session_id, language=None)
        if st.button("Xoá dữ liệu phiên này", type="secondary"):
            store.delete(st.session_state.session_id)
            del st.session_state.session_id
            st.rerun()
        if st.button("Bắt đầu một phiên khác"):
            del st.session_state.session_id
            st.rerun()
    else:
        with st.expander("Mở lại phiên local bằng mã"):
            resume_id = st.text_input("Mã phiên")
            if st.button("Mở phiên"):
                try:
                    store.get(resume_id)
                    st.session_state.session_id = resume_id
                    st.rerun()
                except ValueError as error:
                    st.error(str(error))

if "session_id" not in st.session_state:
    left, right = st.columns([3, 2], gap="large")
    with left:
        st.subheader("Chọn chủ đề hôm nay")
        try:
            items = load_bank()
        except ValueError as error:
            st.error(str(error))
            st.stop()
        item_id = st.selectbox(
            "Chủ đề", [i["item_id"] for i in items],
            format_func=lambda item_id: next(i["topic"] for i in items if i["item_id"] == item_id),
        )
        st.info("Bộ đề mới do AI biên soạn · bản nháp dùng thử, đang chờ nhóm rà soát.")
        if not (ROOT / "runtime/knowledge/descriptors.json").exists():
            st.error("Chưa cài Speaking descriptors. Chạy bước setup trong README trước khi bắt đầu.")
        if st.button("Bắt đầu luyện Speaking", type="primary"):
            try:
                session = service().start(item_id)
                st.session_state.session_id = session.session_id
                st.rerun()
            except ValueError as error:
                st.error(str(error))
    with right:
        st.subheader("Một phiên gồm những gì?")
        st.write("**01 · Làm quen** — 4 câu hỏi về bạn và cuộc sống hằng ngày.")
        st.write("**02 · Kể một câu chuyện** — cue card và 1 phút chuẩn bị.")
        st.write("**03 · Thảo luận sâu hơn** — 4 câu hỏi dựa trên điều bạn đã chia sẻ.")
        st.write("**Nhận xét** — 3 tiêu chí từ text, dẫn chứng và gợi ý luyện tập.")
    st.stop()

try:
    session = store.get(st.session_state.session_id)
except ValueError:
    del st.session_state.session_id
    st.rerun()

if session_item(session).get("verification", {}).get("status") == "pending_human_review":
    st.caption("Bộ đề nháp đang dùng thử · chưa được nhóm xác nhận chất lượng.")

practice, history, trace_tab = st.tabs(["Luyện tập", "Các câu đã trả lời", "Tiến trình agent"])
with history:
    for answer in session.answers:
        st.markdown(f"**Part {answer.part} · Câu {answer.turn_id}**")
        st.text(answer.question)
        st.text(answer.text)
        st.divider()
    if not session.answers:
        st.caption("Câu trả lời sẽ xuất hiện tại đây và được lưu sau mỗi lần nộp.")
with trace_tab:
    render_trace(session)
with practice:
    if session.part == "completed":
        render_result(session)
    else:
        total = len(session_item(session)["part1"]) + 5
        st.progress(min(len(session.answers) / total, 1),
                    text=f"Đã trả lời {len(session.answers)}/{total} lượt")
        label = {
            "part1": "Part 1 · Làm quen", "part2_prepare": "Part 2 · Chuẩn bị",
            "part2": "Part 2 · Trả lời dài", "part3": "Part 3 · Thảo luận",
            "assessment": "Đang chờ nhận xét",
        }[session.part]
        st.subheader(label)
        if "future_question_request_blocked" in session.flags:
            st.info("Trong phiên thi, câu hỏi Part 3 chỉ được hiển thị khi đến lượt. Hãy trả lời câu hiện tại.")
        if session.part == "part2_prepare":
            cue = session_item(session)["cue_card"]
            st.text(cue["prompt"])
            for bullet in cue["bullets"]:
                st.write("• " + bullet)
            preparation(session.session_id, session.preparation_started_at)
        elif session.pending_action:
            st.warning("Câu trả lời đã được lưu. Agent cần hoàn tất bước tiếp theo.")
            if st.button("Thử lại bước agent", type="primary"):
                try:
                    with st.status("Agent đang tiếp tục…", expanded=True) as status:
                        service().retry(session.session_id, lambda e: status.write(event_label(e)))
                    st.rerun()
                except (ModelError, AgentError, ValueError) as error:
                    st.error(str(error))
        else:
            st.text(session.current_question)
            with st.form("answer_form", clear_on_submit=True):
                answer_text = st.text_area("Câu trả lời bằng tiếng Anh", height=180, max_chars=6000)
                submitted = st.form_submit_button("Gửi câu trả lời", type="primary")
            if submitted:
                try:
                    with st.status("Đang lưu bài và xử lý…", expanded=True) as status:
                        service().answer(
                            session.session_id, answer_text,
                            lambda event: status.write(event_label(event)),
                        )
                        status.update(label="Đã hoàn tất bước này", state="complete")
                    st.rerun()
                except (ModelError, AgentError, ValueError) as error:
                    st.error(str(error))

st.caption(DISCLAIMER)
