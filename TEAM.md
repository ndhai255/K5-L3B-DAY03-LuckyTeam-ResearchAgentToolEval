# Team

## Thông tin nhóm

- Tên nhóm:
- Lớp: L3A / L3B
- Repo nhóm: `K5-L3A-DAY03-TenNhom-ResearchAgentToolEval` hoặc `K5-L3B-DAY03-TenNhom-ResearchAgentToolEval` (xem [SUBMISSION.md](SUBMISSION.md))
- URL repo, nhánh nộp, commit chốt:

## Thành viên

| STT | Họ tên | MSSV | Email | GitHub | Vai trò |
| --: | ------ | ---- | ----- | ------ | ------- |
|   1 | Nguyễn Đức Hải | 2A202603943 | ndhai255.work@gmail.com | `ndhai255` | Team Leader — Prompt & Version (v0 → v3) |
|   2 |        |      |       |        |         |

## Cá nhân

Mỗi thành viên đồng thời tạo một báo cáo riêng trong `report/` theo dạng:

```text
report/team/MSSV_HoTen.md
```

Ví dụ: `report/team/20241234_NguyenVanAn.md`.

Sao chép mục dưới đây cho từng thành viên.

## NguyenDucHai-2A202603943 (Leader)

### Phần việc phụ trách

- Vai trò: Prompt & Version (v0 → v3). Checkpoint: CP1, CP2.
- Đầu việc: chạy baseline v0; sửa `starter_v0/artifacts/system_prompt.md` và `starter_v0/artifacts/tools.yaml`; chạy v1, v2, v3; ghi `starter_v0/artifacts/version_log.csv`; viết bảng B1 trong `report/team/group_report.md`.
- Leader: tạo và quản lý repo nhóm, merge nhánh vào `main`.

### Đóng góp cụ thể

- **v0 (CP1):** chạy base eval với artifact gốc trên OpenAI `gpt-4o-mini` (temperature 0): 13/20 PASS, `case_accuracy` 0.65. Chia 7 case FAIL thành 5 case do prompt starter (R08, R10, R11, R12, R14) và 2 case do description tham số của `lookup` (R03, R13), làm cơ sở cho v1 và v2.
- **v1 — `system_prompt.md`:** bỏ các chỉ dẫn xấu của starter (đoán tài khoản, bịa URL, gửi ngay, ép một tool trong một bước); thêm rule hỏi lại bằng `clarify`, xác nhận `yes_no` trước khi `send`, không gọi tool cho câu ngoài phạm vi. `case_accuracy` 0.65 → 0.80; sửa R03, R08, R10, R14; gây lỗi mới M06.
- **v2 — `tools.yaml`:** viết lại description cả 10 tool (làm gì / khi nào dùng / khi nào không) và convention từng tham số (`lookup.query`, `lookup.topic="news"`, `timeframe`, `clarify.response_type` bắt buộc, boundary xác nhận của `send`). `case_accuracy` 0.80 → 0.90; sửa R11, R13.
- **v3 — `system_prompt.md`:** thu hẹp rule nhiều nguồn và thêm rule "lượt sau ghi đè lượt trước". Sửa M06 (`multiturn_accuracy` 0.83 → 1.00) nhưng gây lỗi mới R10 nên `case_accuracy` giữ 0.90. R12 FAIL ở cả 3 version (model hỏi nội dung bằng `text` thay vì xin xác nhận `yes_no`).
- **Báo cáo:** ghi 4 dòng v0–v3 vào `version_log.csv` (hash, giả thuyết, metric trước/sau, run file); viết bảng B1, bảng so sánh chỉ số và phân tích từng version; đưa bảng B2 (7 case FAIL của v0) vào `group_report.md`.

### Bằng chứng

- Commit `f9111d8` ("finish-CP1, CP2") và commit merge `3335c7c` (Pull Request #1, `feat/cp1-cp2` → `main`).
- Run (cả 4 hợp lệ: 20/20 case, 0 lỗi provider): [`v0`](starter_v0/runs/v0_B_base_openai_20261110T181546506674.json), [`v1`](starter_v0/runs/v1_B_base_openai_20261110T184119766103.json), [`v2`](starter_v0/runs/v2_B_base_openai_20261110T184931003075.json), [`v3`](starter_v0/runs/v3_B_base_openai_20261110T185149151645.json).
- [`starter_v0/artifacts/version_log.csv`](starter_v0/artifacts/version_log.csv) (dòng v0–v3), [`system_prompt.md`](starter_v0/artifacts/system_prompt.md), [`tools.yaml`](starter_v0/artifacts/tools.yaml).
- `pytest tests/test_tool_contract.py` tại commit `f9111d8`: 55 passed.
- Báo cáo cá nhân: [`report/team/2A202603943_NguyenDucHai.md`](report/team/2A202603943_NguyenDucHai.md).
