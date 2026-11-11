# Báo cáo cá nhân — NguyenDucHai-2A202603943

## 1. Thông tin thành viên

- Họ tên: Nguyễn Đức Hải
- MSSV: 2A202603943
- Email: ndhai255.work@gmail.com
- GitHub: `ndhai255`
- Lớp / Nhóm: K5-L3B / LuckyTeam
- Vai trò: Team Leader — Prompt & Version (v0 → v3)
- Checkpoint phụ trách: CP1, CP2

## 2. Phần việc phụ trách

Theo phân công của nhóm:

1. **CP1 — Baseline v0:** cấu hình provider, chạy base eval với `system_prompt.md` và `tools.yaml` của starter (chưa sửa), ghi dòng v0 vào `version_log.csv`.
2. **CP2 — Tối ưu v1 → v3:** sửa `starter_v0/artifacts/system_prompt.md` và `starter_v0/artifacts/tools.yaml`, mỗi version chỉ thử một giả thuyết; chạy lại base eval cho v1, v2, v3; ghi hash, giả thuyết và metric trước/sau vào `starter_v0/artifacts/version_log.csv`.
3. **Báo cáo:** viết bảng B1 (Version Evidence) và phần phân tích từng version trong `report/team/group_report.md`.
4. **Leader:** tạo và quản lý repo nhóm, merge nhánh vào `main`.

## 3. Đóng góp cụ thể

Toàn bộ run dùng OpenAI `gpt-4o-mini` (`--provider openai`, temperature 0), bộ base 20 case. Cả 4 run đều hợp lệ: `measured_cases == total_cases == 20`, `provider_error_cases == 0`.

### 3.1. Tổng quan các version

| Version | Artifact đổi | `prompt_hash` / `tools_hash` | `case_accuracy` | Case được sửa | Case hỏng thêm |
|---|---|---|---:|---|---|
| v0 | baseline | `f0c107a9d7a1` / `41a2894f8ad1` | 0.65 | — | 7 FAIL: R03, R08, R10, R11, R12, R13, R14 |
| v1 | `system_prompt.md` | **`c396dd255888`** / `41a2894f8ad1` | 0.80 | R03, R08, R10, R14 | M06 |
| v2 | `tools.yaml` | `c396dd255888` / **`8ee23b5594df`** | 0.90 | R11, R13 | — |
| v3 | `system_prompt.md` | **`83c2d72ee7b1`** / `8ee23b5594df` | 0.90 | M06 | R10 |

Mỗi version chỉ đổi một hash so với version trước (chữ đậm), nên thay đổi metric có thể gắn với đúng một artifact.

### 3.2. CP1 — Baseline v0

- Chạy base eval v0 với artifact gốc: 13/20 PASS, `case_accuracy` 0.65, `tool_routing_accuracy` 0.75, `argument_accuracy` 0.65, `multiturn_accuracy` 1.00.
- Chia 7 case FAIL thành 2 nhóm nguyên nhân, làm cơ sở cho thứ tự sửa:
  - 5 case do chỉ dẫn xấu trong prompt starter: R10 (đoán tài khoản `sama`), R11 (bịa URL `example.com`), R12 (gọi `send` ngay không hỏi), R08 và R14 (câu ngoài phạm vi nhưng vẫn gọi `send`). → sửa ở **v1** (`system_prompt.md`).
  - 2 case do description tham số của `lookup` mơ hồ: R03 (thêm chữ "news" vào `query`), R13 (thiếu `topic="news"`). → sửa ở **v2** (`tools.yaml`).

### 3.3. v1 — Sửa `system_prompt.md`

- **Bỏ** toàn bộ chỉ dẫn xấu của starter: "đừng hỏi lại, cứ đoán", "chọn tài khoản nổi tiếng như Sam Altman", "giả định một URL", "gửi/đăng ngay", "luôn xong trong một bước, chọn một tool".
- **Thêm** 4 nhóm rule:
  - Thiếu tài khoản hoặc URL → gọi `clarify(response_type="text")`, không đoán; đọc lượt trước trước khi hỏi.
  - Gửi/đăng → gọi `clarify(response_type="yes_no")` trước, chỉ gọi `send(confirmed=true)` sau khi user đồng ý ở lượt trước.
  - Câu ngoài phạm vi research (toán, code) → không gọi tool, từ chối ngắn gọn; không dùng `send` để trả lời user.
  - Nhiều nguồn và hội thoại nhiều lượt.
- **Kết quả:** 0.65 → 0.80. Sửa được R08, R10, R14 như giả thuyết; R03 cũng PASS dù không nhắm tới (có thể do dao động của model). R11, R12 mới đúng một phần: đã gọi `clarify` (routing 0.75 → 0.95) nhưng sai `response_type`. Có thêm lỗi mới M06: user nói "bỏ Twitter" nhưng model vẫn gọi `social_search`, khả năng cao do rule "nhiều nguồn → gọi đủ tool" quá rộng.

### 3.4. v2 — Sửa `tools.yaml`

- Viết lại description của cả 10 tool theo cùng khung: làm gì, khi nào dùng, khi nào không dùng (chỉ sang tool đúng).
- Ghi rõ convention tham số, nhắm vào các lỗi tham số còn lại sau v1:
  - `lookup.query`: chỉ chứa từ khóa chủ đề, không thêm "tin tức", "news", "hôm nay".
  - `lookup.topic`: luôn truyền; `news` khi hỏi tin tức/thời sự. `lookup.timeframe`: bảng quy đổi "hôm nay" → `day`, "tuần này" → `week`…
  - `clarify.response_type`: chuyển thành **bắt buộc**; `text` để hỏi thông tin còn thiếu, `yes_no` cho mọi yêu cầu gửi/đăng.
  - `timeline.screenname`: handle không có `@`; `social_search.search_type`: `Top` khi user muốn bài nổi bật, còn lại `Latest`.
  - `send`: ghi boundary ngay trong description ("CHỈ gọi sau `clarify` yes_no và user đã đồng ý"); `confirmed=true` chỉ khi user đã đồng ý.
- **Kết quả:** 0.80 → 0.90. Sửa được R11 (có `response_type="text"`) và R13 (có `topic="news"`). R12 vẫn FAIL: model hỏi nội dung bản tin bằng `clarify(response_type="text")` thay vì xin xác nhận `yes_no`. Hành vi này an toàn (không gửi gì) nhưng khác với kỳ vọng của eval.

### 3.5. v3 — Sửa lại `system_prompt.md`

- Thu hẹp rule nhiều nguồn: chỉ gọi nhiều tool khi user yêu cầu rõ nhiều nguồn, không tự thêm nguồn.
- Thêm rule "lượt sau ghi đè lượt trước": user bỏ hoặc đổi nguồn thì chỉ gọi tool của nguồn mới; các thông tin khác (chủ đề, tài khoản, số lượng) vẫn giữ.
- **Kết quả:** `case_accuracy` giữ 0.90. Sửa được M06 (`multiturn_accuracy` 0.83 → 1.00) và R13 vẫn PASS, đúng giả thuyết. Nhưng có lỗi mới ở R10 ("Tóm tắt 5 tweet mới nhất giúp mình"): model gọi `social_search(query="")` thay vì `clarify`. Mình kiểm tra thêm bằng cách gọi model 5 lần cho câu này (không chạy tool): prompt v2 cho `clarify` 5/5 lần, prompt v3 cho `social_search` 5/5 lần. Vậy lỗi ổn định và do thay đổi của v3. Giả thuyết: các ví dụ mới trong rule ("tìm thêm tweet", "chỉ xem trên Twitter") khiến model gắn chữ "tweet" với `social_search`.

### 3.6. Ghi log và báo cáo

- Ghi 4 dòng v0–v3 vào `version_log.csv`: `artifact_version`, hash, lý do, giả thuyết, metric trước/sau, đường dẫn run.
- Viết bảng B1, bảng so sánh 4 chỉ số qua các version, và phần "Kết quả vX so với vY" cho từng version trong `group_report.md`. Ghi cả các regression (M06 ở v1, R10 ở v3) và case chưa sửa được (R12).
- Đưa bảng B2 (Failure Analysis 7 case FAIL của v0) vào group report trong cùng commit.
- Sau khi sửa `tools.yaml`, chạy `pytest tests/test_tool_contract.py` để chắc tên tool và tham số vẫn khớp registry.

## 4. Bằng chứng

- **Commit / PR:**
  - `f9111d8` — "finish-CP1, CP2": `system_prompt.md`, `tools.yaml`, `version_log.csv`, 4 run JSON, B1 và B2 trong `group_report.md`.
  - `3335c7c` — merge Pull Request #1 (`feat/cp1-cp2` → `main`).
- **Artifact:**
  - [`starter_v0/artifacts/system_prompt.md`](../../starter_v0/artifacts/system_prompt.md): bản v3 do mình viết nằm ở commit `f9111d8` (hash `83c2d72ee7b1`). Bản hiện tại trên `main` là v4 (hash `1bf7d3977ea9`), do thành viên CP3/CP4 bổ sung rule cho `save_note` và `calculator`.
  - [`starter_v0/artifacts/tools.yaml`](../../starter_v0/artifacts/tools.yaml) (khai báo 10 tool có sẵn là bản v2 do mình viết; khai báo tool mới do thành viên phụ trách CP3/CP4 thêm)
  - [`starter_v0/artifacts/version_log.csv`](../../starter_v0/artifacts/version_log.csv) (dòng v0–v3)
- **Run JSON (đều hợp lệ, 20/20 case, 0 lỗi provider):**
  - v0: [`runs/v0_B_base_openai_20261110T181546506674.json`](../../starter_v0/runs/v0_B_base_openai_20261110T181546506674.json)
  - v1: [`runs/v1_B_base_openai_20261110T184119766103.json`](../../starter_v0/runs/v1_B_base_openai_20261110T184119766103.json)
  - v2: [`runs/v2_B_base_openai_20261110T184931003075.json`](../../starter_v0/runs/v2_B_base_openai_20261110T184931003075.json)
  - v3: [`runs/v3_B_base_openai_20261110T185149151645.json`](../../starter_v0/runs/v3_B_base_openai_20261110T185149151645.json)
- **Báo cáo nhóm:** mục B1 và B2 trong [`group_report.md`](group_report.md).
- **Test:** tại commit `f9111d8`, `pytest tests/test_tool_contract.py` → 55 passed; `pytest` toàn bộ → 62 passed, 17 skipped (các test skipped là TODO của CP3, thuộc phần tool mới).
- **AI/công cụ đã dùng và cách tự kiểm tra kết quả:**
  - Claude Code: hỗ trợ soạn báo cáo cá nhân này và đối chiếu số liệu.
  - Cách tự kiểm tra: đọc `summary` của từng run JSON để chắc `provider_error_cases == 0` và `measured_cases == total_cases` trước khi dùng làm bằng chứng; so `prompt_hash`/`tools_hash` giữa các version để chắc mỗi version chỉ đổi một artifact; đọc `results[*].result` để lấy tool call thực tế của từng case FAIL thay vì chỉ dựa vào nhãn `failure_type` của eval; chạy lại contract test sau mỗi lần sửa `tools.yaml`.

## 5. Tự đánh giá

**Làm được:**
- Đủ 4 run hợp lệ, mỗi version đổi đúng một artifact và có giả thuyết dựa trên case FAIL cụ thể của version trước.
- `case_accuracy` tăng từ 0.65 lên 0.90, `tool_routing_accuracy` từ 0.75 lên 0.95.
- Ghi trung thực cả kết quả xấu: v1 gây lỗi M06, v3 không tăng điểm và gây lỗi R10.

**Hạn chế:**
- R12 FAIL ở cả v1, v2, v3. Model luôn hỏi nội dung bản tin (`text`) thay vì xin xác nhận (`yes_no`), dù cả prompt lẫn description đều nói rõ.
- Lỗi R10 do v3 gây ra chưa được sửa.
- R08 và R14 PASS chỉ vì không gọi tool; model vẫn giải toán và viết code thay vì từ chối. Eval không chấm phần này, cần review thủ công.
- Phép thử 5 lần cho R10 chỉ chạy nhanh, chưa lưu log vào repo. Mỗi version cũng chỉ chạy eval 1 lần, nên thay đổi nhỏ như R03 ở v1 chưa phân biệt được với dao động của model.

**Nếu có thêm một vòng:**
- v4 (`system_prompt.md`): sửa R10 bằng rule "yêu cầu về tweet mà không có tài khoản hay chủ đề → `clarify`", và đổi các ví dụ trong rule nhiều nguồn để không dùng chữ "tweet".
- v5: thử sửa R12 bằng ví dụ cụ thể "đăng bản tin này lên Telegram" → `clarify(response_type="yes_no")`.
- Mỗi giả thuyết vẫn là một version riêng, chạy eval nhiều lần cho các case nghi là dao động.

**Bài học:** Sửa một giả thuyết mỗi version giúp tìm được nguyên nhân của regression (M06 do rule mới ở v1, R10 do ví dụ mới ở v3). Thêm rule hay ví dụ vào prompt có thể sửa một case nhưng làm hỏng case khác, nên phải chạy lại toàn bộ eval sau mỗi lần sửa.
