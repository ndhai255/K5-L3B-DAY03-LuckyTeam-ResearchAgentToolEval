from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from chat import assistant_tool_message, now_iso, safe_slug, tool_results_message, trim_history, write_transcript
from providers.base import ToolCall
from tools import TOOL_FUNCTIONS
from versioning import artifact_version_dict, build_artifact_version

# Immutable set of side-effect tools strictly forbidden from executing on public Web UI
BLOCKED_SIDE_EFFECT_TOOLS = frozenset({"send"})

__all__ = [
    "BLOCKED_SIDE_EFFECT_TOOLS",
    "safe_execute_tool_call",
    "sanitize_provider_error",
    "safe_run_model_tool_loop",
    "create_session_transcript",
    "append_transcript_turn",
]


def safe_execute_tool_call(
    call: ToolCall,
    *,
    blocked_tools: frozenset[str] = BLOCKED_SIDE_EFFECT_TOOLS,
) -> dict[str, Any]:
    """Execute a single tool call with fail-closed safety for side-effect tools.

    Crucially, this function does NOT mutate global state, does NOT monkey-patch
    chat.py or TOOL_FUNCTIONS, and remains 100% thread-safe across concurrent sessions.
    """
    if call.name in blocked_tools:
        return {
            "tool": call.name,
            "args": call.args,
            "result": {
                "error": "SafetyBlocked",
                "message": (
                    f"Thực thi công cụ tác dụng phụ (side-effect) '{call.name}' bị chặn hoàn toàn "
                    "trên Web UI công khai để bảo vệ an toàn hệ thống."
                ),
            },
        }

    func = TOOL_FUNCTIONS.get(call.name)
    if not func:
        return {
            "tool": call.name,
            "args": call.args,
            "result": {
                "error": "unknown_tool",
                "message": f"No local implementation for {call.name}",
            },
        }

    try:
        result = func(**call.args)
    except Exception as exc:
        result = {"error": type(exc).__name__, "message": str(exc)}

    return {"tool": call.name, "args": call.args, "result": result}


def sanitize_provider_error(exc: Exception) -> tuple[str, str]:
    """Sanitize provider exceptions into a user-friendly Vietnamese message and a clean category.

    Prevents raw JSON payloads, stack traces, internal URLs, or credentials from leaking
    onto the public UI.

    Returns:
        (user_friendly_message, error_category)
    """
    raw_str = str(exc)
    exc_type = type(exc).__name__

    # 503 Service Unavailable / Model Overloaded
    if "503" in raw_str or "UNAVAILABLE" in raw_str or "overloaded" in raw_str.lower():
        return (
            "Dịch vụ AI (Gemini) đang quá tải tạm thời (503 Service Unavailable). "
            "Vui lòng đợi vài giây và gửi lại câu hỏi.",
            "ServiceUnavailable503",
        )
    # 429 Rate Limit / Quota Exceeded
    if "429" in raw_str or "RESOURCE_EXHAUSTED" in raw_str or "rate limit" in raw_str.lower():
        return (
            "Đã vượt quá giới hạn lượt gọi (429 Rate Limit / Quota Exceeded). "
            "Vui lòng thử lại sau giây lát hoặc chuyển đổi Provider.",
            "RateLimit429",
        )
    # 401 / 403 Authentication / Permission
    if any(k in raw_str for k in ("401", "403", "API_KEY_INVALID", "PERMISSION_DENIED")):
        return (
            "Khóa API không hợp lệ hoặc không có quyền truy cập (401/403 Auth Error). "
            "Vui lòng kiểm tra lại cấu hình khóa trong file .env.",
            "AuthError",
        )
    # Timeout / Network
    if any(k in raw_str.lower() for k in ("timeout", "timed out", "connection error", "connect error")):
        return (
            "Kết nối tới dịch vụ AI bị gián đoạn do hết thời gian chờ (Request Timeout). "
            "Vui lòng kiểm tra kết nối mạng và thử lại.",
            "TimeoutError",
        )
    # Generic fallback (no raw technical JSON leakage)
    return (
        f"Không thể kết nối với Provider ({exc_type}). Vui lòng thử lại sau.",
        f"ProviderError_{exc_type}",
    )


def safe_run_model_tool_loop(
    *,
    provider: Any,
    messages: list[dict[str, str]],
    tools: list[dict[str, Any]],
    model: str | None,
    max_tool_rounds: int,
    blocked_tools: frozenset[str] = BLOCKED_SIDE_EFFECT_TOOLS,
) -> dict[str, Any]:
    """Isolated, concurrency-safe multi-turn tool calling loop for the Web UI.

    Reuses exact prompt/result formatting helpers from chat.py without mutating
    any global dispatcher or module-level state.
    """
    working_messages = list(messages)
    rounds: list[dict[str, Any]] = []
    all_tool_events: list[dict[str, Any]] = []

    for round_index in range(1, max_tool_rounds + 1):
        response = provider.complete(working_messages, tools, model=model, temperature=0.0)
        calls = response.tool_calls
        round_record: dict[str, Any] = {
            "round": round_index,
            "assistant_text": response.text,
            "tool_calls": [{"name": call.name, "args": call.args} for call in calls],
            "tool_results": [],
        }

        if not calls:
            rounds.append(round_record)
            return {
                "status": "answered",
                "assistant_text": response.text or "",
                "rounds": rounds,
                "tool_events": all_tool_events,
            }

        working_messages.append(assistant_tool_message(response.text, calls))
        non_clarification_events: list[dict[str, Any]] = []

        for call in calls:
            event = safe_execute_tool_call(call, blocked_tools=blocked_tools)
            round_record["tool_results"].append(event)
            all_tool_events.append(event)

            # Detect the clarification / awaiting_user flag
            result = event.get("result", {})
            if isinstance(result, dict) and result.get("awaiting_user"):
                question = result.get("question") or call.args.get("question") or "Bạn bổ sung thêm thông tin nhé."
                rounds.append(round_record)
                return {
                    "status": "waiting_for_user",
                    "assistant_text": question,
                    "rounds": rounds,
                    "tool_events": all_tool_events,
                }

            non_clarification_events.append(event)

        rounds.append(round_record)
        working_messages.append(tool_results_message(non_clarification_events))

    return {
        "status": "max_tool_rounds",
        "assistant_text": f"Stopped after {max_tool_rounds} tool rounds. Inspect the transcript for details.",
        "rounds": rounds,
        "tool_events": all_tool_events,
    }


def create_session_transcript(
    *,
    version_label: str,
    provider_name: str,
    model_name: str | None,
    system_prompt_path: Path,
    tools_path: Path,
    history_window: int = 5,
    max_tool_rounds: int = 4,
    transcripts_dir: Path | None = None,
) -> tuple[str, Path, dict[str, Any]]:
    """Initialize a cumulative conversation transcript adhering to Lab 3 specifications.

    Creates the transcript metadata header and writes the initial file to transcripts/.
    """
    if transcripts_dir is None:
        transcripts_dir = Path(__file__).resolve().parent / "transcripts"
    transcripts_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%dT%H%M%S%f")
    transcript_id = "_".join([
        safe_slug(version_label),
        safe_slug(provider_name),
        timestamp,
    ])
    transcript_path = transcripts_dir / f"{transcript_id}.transcript.json"

    artifact_version = build_artifact_version(version_label, system_prompt_path, tools_path)
    transcript: dict[str, Any] = {
        "transcript_id": transcript_id,
        **artifact_version_dict(artifact_version),
        "provider": provider_name,
        "model": model_name,
        "system_prompt": str(system_prompt_path),
        "tools": str(tools_path),
        "history_window": history_window,
        "max_tool_rounds": max_tool_rounds,
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "turns": [],
    }

    write_transcript(transcript_path, transcript)
    return transcript_id, transcript_path, transcript


def append_transcript_turn(
    transcript: dict[str, Any],
    transcript_path: Path,
    *,
    user_text: str,
    started_at: str,
    ended_at: str,
    status: str,
    assistant_text: str | None,
    rounds: list[dict[str, Any]],
    tool_events: list[dict[str, Any]],
    error: str | None = None,
) -> dict[str, Any]:
    """Append a completed turn record to the transcript and persist atomically to disk."""
    turn_index = len(transcript.get("turns", [])) + 1
    turn_record: dict[str, Any] = {
        "turn_index": turn_index,
        "started_at": started_at,
        "ended_at": ended_at,
        "user": user_text,
        "status": status,
        "assistant_text": assistant_text,
        "rounds": rounds,
        "tool_events": tool_events,
    }
    if error:
        turn_record["error"] = error

    transcript.setdefault("turns", []).append(turn_record)
    write_transcript(transcript_path, transcript)
    return turn_record
