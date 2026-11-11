from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

import streamlit as st

# Ensure starter_v0 root is at the head of sys.path for direct module imports
ROOT = Path(__file__).resolve().parent
sys_path_str = str(ROOT)
if sys.path[:1] != [sys_path_str]:
    if sys_path_str in sys.path:
        sys.path.remove(sys_path_str)
    sys.path.insert(0, sys_path_str)

import importlib
import ui_adapter

# Ensure fresh module reload in long-running Streamlit servers if cached
if not hasattr(ui_adapter, "sanitize_provider_error"):
    ui_adapter = importlib.reload(ui_adapter)

from chat import now_iso, trim_history
from env_loader import load_lab_env
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from ui_adapter import (
    BLOCKED_SIDE_EFFECT_TOOLS,
    append_transcript_turn,
    create_session_transcript,
    safe_run_model_tool_loop,
    sanitize_provider_error,
)
from versioning import build_artifact_version

# Load environment configuration (.env) from starter_v0 directory
load_lab_env(ROOT)

ARTIFACTS_DIR = ROOT / "artifacts"
SYSTEM_PROMPT_PATH = ARTIFACTS_DIR / "system_prompt.md"
TOOLS_YAML_PATH = ARTIFACTS_DIR / "tools.yaml"
TRANSCRIPTS_DIR = ROOT / "transcripts"


def get_provider_key_status(provider_name: str) -> tuple[bool, str]:
    """Check whether the necessary API key for the selected provider is set."""
    key_map = {
        "gemini": "GEMINI_API_KEY",
        "openrouter": "OPENROUTER_API_KEY",
        "openai": "OPENAI_API_KEY",
        "anthropic": "ANTHROPIC_API_KEY",
        "ollama": "OLLAMA_BASE_URL",
    }
    env_var = key_map.get(provider_name, "API_KEY")
    if provider_name == "ollama":
        return True, env_var
    val = os.getenv(env_var, "").strip()
    return bool(val), env_var


def load_dynamic_system_prompt() -> str:
    """Read the current system prompt dynamically from artifacts/."""
    if SYSTEM_PROMPT_PATH.exists():
        return SYSTEM_PROMPT_PATH.read_text(encoding="utf-8")
    return "You are a fast, proactive research assistant with access to tools."


def load_dynamic_tools(*, exclude_side_effects: bool = True) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Load tool declarations and return (all_tools, safe_tools) in OpenAI format."""
    if not TOOLS_YAML_PATH.exists():
        return [], []
    declarations = load_tool_declarations(TOOLS_YAML_PATH)
    all_openai_tools = to_openai_tools(declarations)
    if exclude_side_effects:
        # Exclude blocked side-effect tools from schema exposed to the model
        safe_tools = [
            t for t in all_openai_tools
            if t.get("function", {}).get("name") not in BLOCKED_SIDE_EFFECT_TOOLS
        ]
        return all_openai_tools, safe_tools
    return all_openai_tools, all_openai_tools


def init_session_state() -> None:
    """Initialize persistent session state variables for chat history, transcripts, and configuration."""
    if "display_messages" not in st.session_state:
        st.session_state.display_messages = []
    if "llm_history" not in st.session_state:
        st.session_state.llm_history = []
    if "current_provider" not in st.session_state:
        st.session_state.current_provider = "gemini"
    if "current_model" not in st.session_state:
        st.session_state.current_model = "gemini-3.5-flash-lite"
    if "version_label" not in st.session_state:
        st.session_state.version_label = "v0"
    if "history_window" not in st.session_state:
        st.session_state.history_window = 5
    if "max_tool_rounds" not in st.session_state:
        st.session_state.max_tool_rounds = 4

    # Initialize transcript session if not already active
    if "transcript" not in st.session_state or "transcript_path" not in st.session_state:
        start_new_transcript_session(
            provider_name=st.session_state.current_provider,
            model_name=st.session_state.current_model,
            version_label=st.session_state.version_label,
            history_window=st.session_state.history_window,
            max_tool_rounds=st.session_state.max_tool_rounds,
        )


def start_new_transcript_session(
    *,
    provider_name: str,
    model_name: str | None,
    version_label: str,
    history_window: int,
    max_tool_rounds: int,
) -> None:
    """Start a fresh conversation transcript file and reset state."""
    tid, tpath, tdata = create_session_transcript(
        version_label=version_label,
        provider_name=provider_name,
        model_name=model_name,
        system_prompt_path=SYSTEM_PROMPT_PATH,
        tools_path=TOOLS_YAML_PATH,
        history_window=history_window,
        max_tool_rounds=max_tool_rounds,
        transcripts_dir=TRANSCRIPTS_DIR,
    )
    st.session_state.transcript_id = tid
    st.session_state.transcript_path = tpath
    st.session_state.transcript = tdata


def render_tool_events(events: list[dict[str, Any]]) -> None:
    """Render real tool events in an expandable trace container."""
    if not events:
        return
    with st.expander(f"🛠️ Đã điều phối {len(events)} công cụ (Tool Execution Trace)", expanded=False):
        for idx, event in enumerate(events, start=1):
            tool_name = event.get("tool", "unknown")
            args = event.get("args", {})
            result = event.get("result", {})

            st.markdown(f"**#{idx}. Công cụ:** `{tool_name}`")
            if args:
                st.caption("Tham số đầu vào (Arguments):")
                st.json(args)

            if isinstance(result, dict) and result.get("error"):
                st.error(f"Trạng thái: Lỗi [{result.get('error')}] — {result.get('message', '')}")
            elif isinstance(result, dict) and result.get("awaiting_user"):
                st.warning(f"Trạng thái: 🟡 Cần làm rõ — {result.get('question', 'Yêu cầu thêm thông tin')}")
            else:
                st.caption("Kết quả trả về (Tool Result):")
                st.json(result)
            st.markdown("---")


def main() -> None:
    st.set_page_config(
        page_title="LuckyTeam Research Agent",
        page_icon="🤖",
        layout="wide",
    )

    init_session_state()

    # --- SIDEBAR CONFIGURATION ---
    with st.sidebar:
        st.title("🤖 LuckyTeam Agent")
        st.caption("VinUni AI20k — Day 03 Lab (K5-L3B)")
        st.markdown("---")

        st.subheader("Cấu hình Model Provider")
        # Gemini is default as verified
        provider_options = ["gemini", "openrouter", "openai", "anthropic", "ollama"]
        default_idx = provider_options.index(st.session_state.current_provider) if st.session_state.current_provider in provider_options else 0

        provider_name = st.selectbox(
            "Chọn LLM Provider",
            options=provider_options,
            index=default_idx,
            help="Gemini là provider mặc định đã được cấu hình và kiểm thử thành công.",
        )

        # Default model override set to gemini-3.5-flash-lite
        default_model_val = "gemini-3.5-flash-lite" if provider_name == "gemini" else ""
        model_override = st.text_input(
            "Tên Model (Tùy chọn ghi đè)",
            value=default_model_val,
            placeholder="Để trống để dùng model mặc định",
            help="Ví dụ: gemini-3.5-flash-lite, openai/gpt-4o-mini...",
        ).strip() or None

        version_label = st.text_input(
            "Version Tag",
            value=st.session_state.version_label,
            help="Nhãn phiên bản artifact (v0, v1, v2, v3)",
        ).strip() or "v0"

        # Check if provider or model or version changed -> reset session and transcript
        if (
            st.session_state.current_provider != provider_name
            or st.session_state.current_model != (model_override or "")
            or st.session_state.version_label != version_label
        ):
            st.session_state.current_provider = provider_name
            st.session_state.current_model = model_override or ""
            st.session_state.version_label = version_label
            st.session_state.display_messages = []
            st.session_state.llm_history = []
            start_new_transcript_session(
                provider_name=provider_name,
                model_name=model_override,
                version_label=version_label,
                history_window=st.session_state.history_window,
                max_tool_rounds=st.session_state.max_tool_rounds,
            )
            st.toast("Đã chuyển đổi Provider / Model — Khởi tạo phiên Transcript mới.", icon="🔄")

        # Provider API Key status check (no secret exposure)
        has_key, key_var = get_provider_key_status(provider_name)
        if has_key:
            st.success(f"🔑 `{key_var}`: Đã cấu hình", icon="✅")
        else:
            st.error(f"⚠️ `{key_var}`: Chưa tìm thấy trong .env", icon="🚨")

        st.markdown("---")
        st.subheader("Tham số Vòng lặp Agent")
        max_tool_rounds = st.slider("Số vòng Tool tối đa (max_tool_rounds)", min_value=1, max_value=8, value=4)
        history_window = st.slider("Cửa sổ lịch sử đàm thoại (history_window)", min_value=1, max_value=10, value=5)
        st.session_state.max_tool_rounds = max_tool_rounds
        st.session_state.history_window = history_window

        st.markdown("---")
        st.subheader("Lưu Vết Transcript (Lab 3 Logging)")
        num_turns = len(st.session_state.transcript.get("turns", []))
        st.markdown(f"**ID:** `{st.session_state.transcript_id}`")
        st.markdown(f"**Số turns đã lưu:** `{num_turns}`")
        st.caption(f"📁 `{st.session_state.transcript_path.name}`")

        # Download transcript button
        transcript_json_str = json.dumps(st.session_state.transcript, ensure_ascii=False, indent=2, default=str)
        st.download_button(
            "📥 Tải Transcript (.json)",
            data=transcript_json_str,
            file_name=st.session_state.transcript_path.name,
            mime="application/json",
            use_container_width=True,
        )

        st.markdown("---")
        st.subheader("An toàn & Kiểm soát Side-effects")
        st.info(
            "🛡️ **Safety Guard: Active**\n\n"
            "Công cụ gửi tin (`send`) bị loại khỏi schema và bị chặn thực thi 100% "
            "qua `ui_adapter.py` mà không can thiệp module toàn cục.",
            icon="🔒",
        )

        st.markdown("---")
        st.subheader("Quản lý Phiên & Dữ liệu")
        col_clear, col_reload = st.columns(2)
        with col_clear:
            if st.button("🗑️ Xóa chat", use_container_width=True):
                st.session_state.display_messages = []
                st.session_state.llm_history = []
                start_new_transcript_session(
                    provider_name=provider_name,
                    model_name=model_override,
                    version_label=version_label,
                    history_window=history_window,
                    max_tool_rounds=max_tool_rounds,
                )
                st.rerun()
        with col_reload:
            if st.button("🔄 Nạp lại File", use_container_width=True, help="Nạp lại system_prompt.md & tools.yaml từ đĩa"):
                st.toast("Đã nạp lại artifacts từ đĩa.", icon="🔄")
                st.rerun()

    # --- MAIN CHAT VIEW ---
    st.title("🤖 LuckyTeam Autonomous Research Agent")
    st.caption("VinUni AI20k Day 03 — Research Agent Tool Evaluation (K5-L3B)")

    # Read dynamic prompt and schemas
    system_prompt = load_dynamic_system_prompt()
    all_tools, safe_tools = load_dynamic_tools(exclude_side_effects=True)

    # Calculate current artifact signature for transparency
    artifact_sig = build_artifact_version(version_label, SYSTEM_PROMPT_PATH, TOOLS_YAML_PATH)
    st.caption(
        f"📦 **Artifact Version:** `{artifact_sig.artifact_version}` | "
        f"**Prompt SHA:** `{artifact_sig.prompt_hash[:12]}` | "
        f"**Tools SHA:** `{artifact_sig.tools_hash[:12]}` | "
        f"**Tools khả dụng:** `{len(safe_tools)}` tools"
    )

    if not has_key:
        st.warning(
            f"⚠️ **Chưa cấu hình `{key_var}`:** Vui lòng tạo file `starter_v0/.env` và điền khóa API "
            f"để Agent có thể kết nối với Provider `{provider_name}`.",
            icon="⚠️",
        )

    st.markdown("---")

    # Render previous conversation history from display_messages
    for msg in st.session_state.display_messages:
        with st.chat_message(msg["role"]):
            if msg.get("tool_events"):
                render_tool_events(msg["tool_events"])
            st.markdown(msg["content"])
            if msg.get("status") == "waiting_for_user":
                st.caption("🟡 *Agent đang chờ phản hồi làm rõ thông tin từ bạn.*")

    # Handle new user prompt
    if prompt := st.chat_input("Nhập câu hỏi nghiên cứu hoặc yêu cầu công việc..."):
        # 1. Display user message
        st.session_state.display_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # 2. Check provider readiness
        if not has_key:
            error_msg = f"Không thể thực thi yêu cầu: Biến môi trường `{key_var}` chưa được thiết lập trong `starter_v0/.env`."
            st.session_state.display_messages.append({
                "role": "assistant",
                "content": error_msg,
                "status": "error",
            })
            with st.chat_message("assistant"):
                st.error(error_msg)
            return

        # 3. Build messages payload according to contract
        messages = [
            {"role": "system", "content": system_prompt},
            *trim_history(st.session_state.llm_history, window=history_window),
            {"role": "user", "content": prompt},
        ]

        started_at = now_iso()

        # 4. Execute real Agent using safe, isolated ui_adapter (no global monkey-patching)
        with st.chat_message("assistant"):
            status_placeholder = st.status("Agent đang suy luận và điều phối công cụ...", expanded=True)
            try:
                provider = make_provider(provider_name)

                result = safe_run_model_tool_loop(
                    provider=provider,
                    messages=messages,
                    tools=safe_tools,
                    model=model_override,
                    max_tool_rounds=max_tool_rounds,
                    blocked_tools=BLOCKED_SIDE_EFFECT_TOOLS,
                )

                ended_at = now_iso()
                status = result.get("status", "answered")
                assistant_text = result.get("assistant_text") or ""
                tool_events = result.get("tool_events") or []

                # Update status indicator
                if status == "waiting_for_user":
                    status_placeholder.update(
                        label=f"🟡 Agent cần bạn làm rõ thông tin (Đã gọi {len(tool_events)} công cụ)",
                        state="complete",
                        expanded=False,
                    )
                elif status == "answered":
                    status_placeholder.update(
                        label=f"🟢 Đã hoàn tất nghiên cứu (Đã gọi {len(tool_events)} công cụ)",
                        state="complete",
                        expanded=False,
                    )
                else:
                    status_placeholder.update(
                        label=f"🟠 Dừng lại: {status} (Đã gọi {len(tool_events)} công cụ)",
                        state="complete",
                        expanded=False,
                    )

                # Render real tool execution trace
                if tool_events:
                    render_tool_events(tool_events)

                # Render final assistant response
                st.markdown(assistant_text)
                if status == "waiting_for_user":
                    st.caption("🟡 *Agent đang chờ phản hồi làm rõ thông tin từ bạn.*")

                # Update clean LLM history (only clean user and assistant texts)
                st.session_state.llm_history.append({"role": "user", "content": prompt})
                st.session_state.llm_history.append({"role": "assistant", "content": assistant_text})

                # Update UI display history
                st.session_state.display_messages.append({
                    "role": "assistant",
                    "content": assistant_text,
                    "tool_events": tool_events,
                    "status": status,
                })

                # Persist turn in cumulative transcript file
                append_transcript_turn(
                    st.session_state.transcript,
                    st.session_state.transcript_path,
                    user_text=prompt,
                    started_at=started_at,
                    ended_at=ended_at,
                    status=status,
                    assistant_text=assistant_text,
                    rounds=result.get("rounds", []),
                    tool_events=tool_events,
                )

            except Exception as exc:
                ended_at = now_iso()
                user_friendly_error, error_category = sanitize_provider_error(exc)
                status_placeholder.update(
                    label="⚠️ Dịch vụ AI tạm thời gián đoạn",
                    state="error",
                    expanded=False,
                )
                st.error(user_friendly_error)
                st.info("💡 Bạn có thể gửi lại câu hỏi để thử lại (lịch sử hội thoại trước đó vẫn được bảo toàn nguyên vẹn).")
                st.session_state.display_messages.append({
                    "role": "assistant",
                    "content": user_friendly_error,
                    "status": "provider_error",
                })

                # Persist sanitized error turn in transcript without leaking raw stack trace or secrets
                append_transcript_turn(
                    st.session_state.transcript,
                    st.session_state.transcript_path,
                    user_text=prompt,
                    started_at=started_at,
                    ended_at=ended_at,
                    status="provider_error",
                    assistant_text=None,
                    rounds=[],
                    tool_events=[],
                    error=f"{error_category}: {user_friendly_error}",
                )


if __name__ == "__main__":
    main()
