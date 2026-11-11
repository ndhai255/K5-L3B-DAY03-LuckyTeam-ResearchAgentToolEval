# Báo cáo cá nhân — Nguyễn Anh Quân (2A202603950)

## 1. Thông tin thành viên

- **Họ và tên:** Nguyễn Anh Quân
- **MSSV:** 2A202603950
- **Email:** anhhquan511@gmail.com
- **Vai trò trong nhóm:** Log Analyst & Eval Designer
- **Checkpoint phụ trách:** CP1, CP4

---

## 2. Phần việc phụ trách

Theo phân công trong nhóm (như ghi nhận trong `TEAM.md` và `group_report.md`):
- **Phụ trách Checkpoint 1 (CP1):** Khởi tạo môi trường, kiểm tra preflight kết nối provider, chạy đo lường Baseline `v0`, đọc phân tích toàn bộ file run JSON và xác định các nguyên nhân gốc rễ gây ra lỗi (failure breakdown).
- **Phụ trách Checkpoint 4 (CP4):** Thiết kế bộ dữ liệu đánh giá của nhóm gồm đúng 10 test cases (5 single-turn và 5 multi-turn) trong file `starter_v0/data/eval_group.json`, bao phủ các ca kiểm thử tool mới (`calculator`, `save_note`), trích xuất tham số, ranh giới xác nhận an toàn và từ chối câu hỏi ngoài phạm vi; thực thi lệnh chạy đánh giá `--suite group`.
- **Hỗ trợ Mục B2 & B3 của Báo cáo nhóm (`group_report.md`):** Phân tích các ca FAIL chi tiết, lập giả thuyết tối ưu cho từng version (`v1`, `v2`, `v3`) và hoàn thiện bảng tổng hợp 10 eval cases của nhóm.

---

## 3. Đóng góp cụ thể

### 3.1. Phân tích Log JSON & Đặt giả thuyết cải tiến (CP1 & Mục B2)
- **Khai thác dữ liệu Baseline v0:** Chạy và trích xuất dữ liệu từ run JSON ban đầu (`case_accuracy` 65% - 70%), phân tích chi tiết từng trường hợp thất bại:
  - Nhóm lỗi do prompt starter xấu (5 ca): Model tự ý đoán tài khoản Sam Altman (`R10_missing_handle`), tự bịa URL bài viết (`R11_missing_url`), tự tiện gọi `send` khi chưa có xác nhận từ người dùng (`R12_confirm_before_send`), gọi tool thừa cho câu hỏi ngoài phạm vi (`R08_out_of_scope`, `R14_out_of_scope_coding`).
  - Nhóm lỗi do mô tả tham số trong `tools.yaml` chưa rõ ràng (2 ca): Lặp lại chữ "news" vào query của `lookup` và thiếu tham số `topic="news"` khi tìm kiếm tin tức thời sự (`R03_web_news_routing`, `R13_parallel_web_and_tweets`).
- **Xây dựng giả thuyết tối ưu hóa có bằng chứng:**
  - *Giả thuyết v1:* Loại bỏ triệt để các câu chỉ dẫn ép đoán mò và ép một bước; bổ sung quy tắc gọi `clarify` khi thiếu thông tin và yêu cầu xác nhận `yes_no` trước khi thực thi action tool. (Kết quả: Độ chính xác tăng lên 80%).
  - *Giả thuyết v2:* Chuẩn hóa toàn bộ `description` và convention tham số trong `tools.yaml` (quy định rõ handle không có ký tự `@`, quy định `topic='news'`, `search_type='Top'|'Latest'`). (Kết quả: Độ chính xác tăng lên 90%).
  - *Giả thuyết v3:* Bổ sung cơ chế kế thừa ngữ cảnh (Context Carryover) cho hội thoại đa lượt và thu hẹp quy tắc gọi đồng thời nhiều nguồn. (Kết quả: Đạt 95% - 100%, routing accuracy đạt tuyệt đối 1.0).

### 3.2. Thiết kế và Hoàn thiện bộ 10 Eval Cases của nhóm (CP4 & Mục B3)
Tự tay thiết kế và cấu trúc hóa file `starter_v0/data/eval_group.json` gồm 10 ca kiểm thử độc lập, đảm bảo tuân thủ nghiêm ngặt schema của bài lab và pass 100% `test_tool_contract.py`:
- **5 ca Single-Turn (1 lượt):**
  1. `G01_calculator_routing`: Kiểm tra Agent tự động phân luồng tới tool mới `calculator` khi có biểu thức toán học cần tính toán (`(120 - 80) * 5 / 2`).
  2. `G02_lookup_news_month`: Kiểm tra trích xuất chính xác `topic="news"` và `timeframe="month"` từ cụm từ "trong tháng qua".
  3. `G03_social_search_latest`: Kiểm tra trích xuất tham số `search_type="Latest"` từ yêu cầu "tweet mới nhất".
  4. `G04_missing_timeline_handle`: Xử lý yêu cầu lấy bài đăng nhưng thiếu tài khoản đích -> Bắt buộc Agent gọi `clarify(response_type="text")`.
  5. `G05_out_of_scope_weather`: Câu hỏi dự báo thời tiết ngoài phạm vi nghiên cứu -> Agent từ chối lịch sự, `no_tool: true`.
- **5 ca Multi-Turn (đa lượt hội thoại):**
  6. `GM01_save_note_after_confirmation`: Kiểm tra quy trình an toàn 2 lượt: Lượt 1 yêu cầu lưu ghi chú, Lượt 2 user xác nhận đồng ý -> Agent mới gọi `save_note` với `confirmed=true`.
  7. `GM02_clarify_then_timeline`: Hội thoại 3 lượt dẫn dắt từ yêu cầu chung chung tới việc bổ sung username `sama` và `limit=5`.
  8. `GM03_multiturn_clarify_url`: Hội thoại 3 lượt xin link bài báo nghiên cứu và thực hiện gọi `fetch`.
  9. `GM04_multiturn_timeframe_update`: Duy trì ngữ cảnh hội thoại, cập nhật `timeframe` từ `day` sang `month` trong khi vẫn bảo lưu chủ đề tìm kiếm.
  10. `GM05_multiturn_calculator`: Hội thoại nhiều lượt dẫn dắt tới bài toán tính toán số liệu tài chính qua tool `calculator`.

---

## 4. Bằng chứng

- **Các file trực tiếp đóng góp trong Repository:**
  - `starter_v0/data/eval_group.json`: Cấu trúc và nội dung hoàn chỉnh của 10 eval cases nhóm.
  - `report/team/group_report.md`: Đóng góp hoàn thiện Bảng B2 (Failure Analysis) và Bảng B3 (Team Eval Cases).
  - `starter_v0/artifacts/version_log.csv`: Ghi chép lịch sử đo lường, mã hash và kết quả metric qua các vòng.
- **Commit cá nhân trên Git:**
  - Commit `bde12ba`: *"complete checkpoint 1 to 4 version test"* trên nhánh `feature/CP3`.
- **File kết quả đánh giá (Run JSON):**
  - Các file run thực tế sinh ra trong thư mục `starter_v0/runs/`:
    - Baseline v0: `runs/v0_B_base_openrouter_20261110T190314834161.json` (70% accuracy)
    - Version v1: `runs/v1_B_base_openrouter_20261110T191226027013.json` (80% accuracy)
    - Version v2: `runs/v2_B_base_openrouter_20261110T192254242999.json` (90% accuracy)
    - Version v3: `runs/v3_B_base_openrouter_20261110T192858515309.json` (95% accuracy, 100% routing accuracy)
    - Suite group (CP4): `runs/v3_B_group_openrouter_20261111T091359077950.json` (90% accuracy, 9/10 passed)
- **Công cụ đã sử dụng và phương pháp kiểm chứng:**
  - Sử dụng Python scripting đọc parse các file JSON trong `runs/` để trích xuất `failures` và `observed_mismatch`.
  - Kiểm tra tính hợp lệ bằng test tự động: `pytest tests/test_tool_contract.py` (65/65 test pass).
  - Kiểm tra thực thi bộ test nhóm: `python run_eval.py --suite group --eval-cases data/eval_group.json`.

---

## 5. Tự đánh giá

- **Mức độ hoàn thành:** 100% các mục tiêu và nhiệm vụ được phân công trong Checkpoint 1 và Checkpoint 4.
- **Tính chuẩn xác và kỷ luật khoa học:** Áp dụng chặt chẽ phương pháp tiếp cận dựa trên bằng chứng (evidence-driven); mọi giả thuyết đưa ra đều có số liệu run JSON đối chiếu trước/sau rõ ràng.
- **Chất lượng bộ dữ liệu kiểm thử:** 10 test case được thiết kế chặt chẽ, kiểm thử bao quát từ tool mới, xử lý tham số biên, ranh giới an toàn cho đến hội thoại ngữ cảnh phức tạp.
- **Điểm tự chấm:** 10/10.
