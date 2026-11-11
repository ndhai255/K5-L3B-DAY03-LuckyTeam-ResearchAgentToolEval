# Team

## Thông tin nhóm

- Tên nhóm: **LuckyTeam**
- Lớp: **K5-L3B**
- Repo nhóm: `K5-L3B-DAY03-LuckyTeam-ResearchAgentToolEval` (xem [SUBMISSION.md](SUBMISSION.md))
- URL repo: https://github.com/ndhai255/K5-L3B-DAY03-LuckyTeam-ResearchAgentToolEval
- Nhánh nộp: `main` (tổng hợp từ các nhánh tính năng)
- Commit chốt: commit cuối cùng trên nhánh `main` trước deadline

## Thành viên

| STT | Họ tên | MSSV | Email | GitHub | Vai trò |
| --: | ------ | ---- | ----- | ------ | ------- |
|   1 | Nguyễn Đức Hải | 2A202603943 | ndhai255.work@gmail.com | ndhai255 | Team Leader — Quản trị version, Prompt & Schema v1–v3 |
|   2 | Nguyễn Anh Quân | 2A202603950 | anhhquan511@gmail.com | — | Log Analyst & Eval Designer — Phân tích lỗi benchmark, Thiết kế 10 eval cases nhóm |
|   3 | Vũ Quang Hải | 2A202603935 | haivq96@gmail.com | HaiVuQ | Tool Developer — Phát triển Custom Tool `save_note` & Unit Tests |
|   4 | Tăng Nguyễn Hải Đăng | 2A202603916 | 26ai.dangtnh@vinuni.edu.vn | haidangwork1411 | UI & Integration — Streamlit UI, UI Adapter an toàn, Transcripts & Báo cáo |

> *Ghi chú nguồn xác thực thông tin cá nhân:*
> - Cả 4 thành viên trong nhóm đã hoàn thiện đầy đủ báo cáo cá nhân và xác nhận thông tin chéo trong thư mục `report/team/`:
>   - Nguyễn Đức Hải: [`report/team/2A202603943_NguyenDucHai.md`](report/team/2A202603943_NguyenDucHai.md) (Team Leader, CP1, CP2).
>   - Nguyễn Anh Quân: [`report/team/2A202603950_NguyenAnhQuan.md`](report/team/2A202603950_NguyenAnhQuan.md) (Log Analyst & Eval Designer, CP1, CP4).
>   - Vũ Quang Hải: [`report/team/2A202603935_VuQuangHai.md`](report/team/2A202603935_VuQuangHai.md) (Tool Developer, CP3).
>   - Tăng Nguyễn Hải Đăng: [`report/team/2A202603916_TangNguyenHaiDang.md`](report/team/2A202603916_TangNguyenHaiDang.md) (UI & Integration, CP5).

## Cá nhân

Mỗi thành viên đồng thời tạo một báo cáo riêng trong `report/team/` theo dạng:

```text
report/team/MSSV_HoTen.md
```

---

## Nguyễn Đức Hải (Leader)

### Phần việc phụ trách
- Checkpoint phụ trách: CP1, CP2
- Quản trị kho mã nguồn Git, thiết lập và chạy baseline `v0` (CP1).
- Tối ưu hóa System Prompt (`starter_v0/artifacts/system_prompt.md`) và Schema (`starter_v0/artifacts/tools.yaml`) qua các phiên bản `v1` $\rightarrow$ `v3` (CP2).
- Ghi nhận nhật ký phiên bản và mã băm SHA256 vào `starter_v0/artifacts/version_log.csv`.
- Đo lường và sinh các file kết quả benchmark `runs/v0_...` đến `runs/v3_...` trên mô hình OpenAI `gpt-4o-mini`.

### Đóng góp cụ thể
- Thiết lập 3 vòng lặp tối ưu hóa dựa trên bằng chứng:
  - *Vòng v1:* Sửa `system_prompt.md`, loại bỏ các chỉ dẫn xấu (đoán handle, bịa URL, gửi ngay), bổ sung rule hỏi lại bằng `clarify` và xác nhận trước khi gửi (`case_accuracy` tăng từ 0.65 lên 0.80).
  - *Vòng v2:* Sửa `tools.yaml`, chuẩn hóa mô tả chi tiết và quy ước tham số (`case_accuracy` tăng lên 0.90).
  - *Vòng v3:* Sửa `system_prompt.md`, thu hẹp quy tắc gọi nhiều nguồn và thêm quy tắc lượt sau ghi đè lượt trước, đưa `multiturn_accuracy` trở lại 1.00.
- Soạn thảo và hoàn thiện Mục B1 (Version Evidence) và Mục B2 (Failure Analysis cho 7 ca lỗi v0) trong `report/team/group_report.md`.

### Bằng chứng
- Pull Request #1 (Commit `f9111d8`, commit merge `3335c7c` trên `origin/main`).
- Các file run thực tế: `starter_v0/runs/v0_B_base_openai_20261110T181546506674.json` $\rightarrow$ `v3_B_base_openai_20261110T185149151645.json`.
- File ghi nhật ký: `starter_v0/artifacts/version_log.csv`.
- Báo cáo cá nhân: [`report/team/2A202603943_NguyenDucHai.md`](report/team/2A202603943_NguyenDucHai.md).

---

## NguyenAnhQuan-2A202603950


### Phần việc phụ trách
- Checkpoint: CP1, CP4
- Đầu việc: Đọc run JSON, gán loại lỗi cho case FAIL (B2), đưa giả thuyết cho từng version; viết 10 case eval_group.json (5 single + 5 multi turn), chạy --suite group (B3).

### Đóng góp cụ thể
- Trích xuất dữ liệu run JSON Baseline v0, phân tích phân loại nguyên nhân 7 ca FAIL ở Mục B2.
- Thiết lập giả thuyết cho các vòng tối ưu v1, v2, v3 dựa trên bằng chứng log thật.
- Thiết kế trọn vẹn 10 test cases trong `starter_v0/data/eval_group.json` (5 single-turn + 5 multi-turn) bao quát cả 2 tool mới của nhóm.
- Phát triển thêm công cụ phụ trợ `calculator` (`starter_v0/tools/calculator/tool.py`).

### Bằng chứng
- File `starter_v0/data/eval_group.json` (10 test cases).
- File `report/team/2A202603950_NguyenAnhQuan.md` trên nhánh `origin/feature/CP4`.
- Commit cá nhân `bde12ba` và `6f54458` trên nhánh `origin/feature/CP4`.
- 4 file run OpenRouter: `starter_v0/runs/v0_B_base_openrouter_...json` $\rightarrow$ `v3_...json`.

---

## VuQuangHai-2A202603935 (Tool Developer)

### Phần việc phụ trách
- Checkpoint phụ trách: CP3 (Custom Tool & Unit Tests).
- Phát triển tool `save_note` để lưu ghi chú nghiên cứu cục bộ, kèm tài liệu, khai báo và đăng ký tool.
- Viết unit test cho các luồng chính, guardrail và nhánh lỗi của `save_note`.

### Đóng góp cụ thể
- Xây dựng công cụ `save_note` tại `starter_v0/tools/save_note/tool.py` để lưu ghi chú/tóm tắt Markdown trong thư mục `notes/`, tự động chuẩn hóa đuôi file.
- Thêm guardrail chặn path traversal và input rỗng; chỉ ghi khi `confirmed` là boolean `True`; nếu file đã tồn tại thì không ghi đè cho tới khi người dùng xác nhận riêng qua `overwrite_confirmed=True`.
- Tạo `TOOL.md`, đăng ký tool trong `starter_v0/tools/__init__.py` và khai báo schema/description trong `starter_v0/artifacts/tools.yaml`.
- Viết 10 unit test cho happy path, input không hợp lệ, xác nhận sai kiểu, ghi đè cần xác nhận và lỗi filesystem; cập nhật system prompt để hướng agent tuân thủ các bước xác nhận.
- Cập nhật bằng chứng CP3 trong báo cáo nhóm.

### Bằng chứng
- Thư mục công cụ: `starter_v0/tools/save_note/` (`tool.py`, `TOOL.md`).
- File unit test: `starter_v0/tests/test_tools_todo.py` (10 tests cho `save_note`).
- Commit cá nhân: `56384df` và `02ba4be` trên nhánh `feature/CP3`.
- Báo cáo cá nhân: [`report/team/2A202603935_VuQuangHai.md`](report/team/2A202603935_VuQuangHai.md).
- Kiểm thử: 10 test `save_note` pass. Trên `main` lúc nộp (đã có thêm 3 test `calculator`): 65 test contract pass, toàn suite 85 passed, 14 skipped (stub TODO của các tool có sẵn).

---

## Tăng Nguyễn Hải Đăng (UI & Integration)

### Phần việc phụ trách
- Checkpoint phụ trách: CP5 (Streamlit UI, Adapter an toàn, Transcript logging & Báo cáo kỹ thuật).
- Phát triển ứng dụng Web Streamlit (`starter_v0/app.py`) phục vụ tương tác đàm thoại đa lượt và trực quan hóa Tool Execution Trace.
- Xây dựng module adapter an toàn (`starter_v0/ui_adapter.py`) tách biệt với luồng thực thi chung, chặn gọi công cụ `send` ở runtime tầng UI mà không sửa đổi file dùng chung của `chat.py`.
- Triển khai cơ chế tự động ghi nhận và lưu vết Transcript theo chuẩn bài lab vào `starter_v0/transcripts/`.
- Xử lý các mã lỗi mạng từ nhà cung cấp (Gemini HTTP 503 UNAVAILABLE, 429 Rate Limit) thân thiện bằng tiếng Việt, bảo toàn ngữ cảnh trò chuyện.
- Biên soạn Phần A trong Báo cáo nhóm (`report/team/group_report.md`) và hoàn thiện Báo cáo cá nhân (`report/team/2A202603916_TangNguyenHaiDang.md`).

### Đóng góp cụ thể
- Thiết kế kiến trúc hai tầng bộ nhớ hội thoại: `display_messages` (quản lý hiển thị UI) và `llm_history` (danh sách sạch phục vụ `trim_history`).
- Xây dựng vòng lặp `safe_run_model_tool_loop()` và cơ chế fail-closed chặn `send(confirmed=True)` ở tầng UI.
- Kết nối thành công và kiểm thử preflight với Google Gemini (`gemini-3.5-flash-lite`), thu thập 2 phiên transcript thực nghiệm.
- Xử lý lỗi nạp module khi giao diện reload bằng khai báo `__all__`, chuẩn hóa `sys.path` và cơ chế nạp lại mô-đun chủ động (`importlib.reload`).

### Bằng chứng
- Mã nguồn độc lập: `starter_v0/app.py`, `starter_v0/ui_adapter.py`, `starter_v0/requirements.txt`.
- Dữ liệu thực nghiệm transcript: `starter_v0/transcripts/v0_gemini_20261111T001248833127.transcript.json`, `starter_v0/transcripts/v0_gemini_20261111T004018512852.transcript.json`.
- File báo cáo cá nhân: `report/team/2A202603916_TangNguyenHaiDang.md`.
- Commit cá nhân: `4bd17c9` và `dc11d38` trên nhánh `origin/feat/ui-stream-demo`.
