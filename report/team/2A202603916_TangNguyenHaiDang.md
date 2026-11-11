# Báo cáo cá nhân — 2A202603916_TangNguyenHaiDang

## 1. Thông tin thành viên

- Họ tên: Tăng Nguyễn Hải Đăng
- MSSV: 2A202603916
- Email: 26ai.dangtnh@vinuni.edu.vn
- GitHub: haidangwork1411
- Lớp: K5-L3B
- Nhóm: LuckyTeam
- Nhánh Git công tác: `feat/ui-stream-demo`
- Vai trò phân công: Phát triển Giao diện Streamlit, Tích hợp Hệ thống, Lưu vết Transcript, Báo cáo Kỹ thuật

---

## 2. Phần việc phụ trách

Trong bài thực hành Lab 03, tôi đảm nhiệm vai trò Thành viên 4 của LuckyTeam với các trách nhiệm cụ thể sau:

1. **Phát triển Giao diện Người dùng Web:** Xây dựng ứng dụng web bằng Streamlit ([`starter_v0/app.py`](../../starter_v0/app.py)), hỗ trợ đàm thoại đa lượt (multi-turn chat) và trực quan hóa vết thực thi công cụ (Tool Execution Trace) của Research Agent.
2. **Tích hợp Mô hình và Điều phối Vòng lặp:** Kết nối giao diện với Google Gemini (`gemini-3.5-flash-lite`) làm provider mặc định cho UI (đã vượt qua kiểm thử preflight trực tiếp), đồng thời hỗ trợ chuyển đổi linh hoạt sang OpenRouter và OpenAI.
3. **Thiết kế Module Adapter An toàn:** Xây dựng [`starter_v0/ui_adapter.py`](../../starter_v0/ui_adapter.py) nhằm cách ly hoàn toàn luồng giao diện với logic lõi, kiểm soát việc gọi công cụ `send` ở runtime tầng UI theo nguyên tắc fail-closed mà không can thiệp monkey-patching vào mã nguồn dùng chung của nhóm.
4. **Lưu vết Hội thoại (Transcript Logging):** Tích hợp hàm `write_transcript` từ `chat.py`, tự động lưu vết toàn bộ tiến trình đàm thoại, tham số công cụ và kết quả trả về dưới dạng file JSON chuẩn vào thư mục `starter_v0/transcripts/`.
5. **Xử lý và Làm sạch Lỗi Nhà cung cấp:** Xây dựng hàm `sanitize_provider_error` để nhận diện và chuyển đổi các mã lỗi dịch vụ (Gemini HTTP 503 Service Unavailable, 429 Rate Limit, 401 Auth Error) thành thông điệp tiếng Việt thân thiện, bảo toàn lịch sử trò chuyện và không làm lộ cấu trúc lỗi kỹ thuật ra giao diện.
6. **Báo cáo Kỹ thuật và Kiểm toán Bài nộp:** Biên soạn Phần A trong Báo cáo nhóm ([`report/team/group_report.md`](group_report.md)), hoàn thiện Báo cáo cá nhân và rà soát tính nhất quán của kho mã nguồn trước khi nộp bài.

---

## 3. Đóng góp cụ thể

Trong quá trình thực hiện nhánh `feat/ui-stream-demo`, tôi đã tuần tự hoàn thành các hạng mục kỹ thuật sau:

- **Xây dựng khung giao diện Streamlit (`starter_v0/app.py`):**
  - Tôi thiết kế giao diện đàm thoại với thanh Sidebar hiển thị trạng thái hệ thống, lựa chọn provider/model, cấu hình phiên bản artifact và nút tải file transcript.
  - Thiết kế kiến trúc hai tầng bộ nhớ hội thoại: `display_messages` (quản lý hiển thị tin nhắn và các khối expander chứa vết công cụ cho người dùng) và `llm_history` (danh sách sạch chỉ chứa các cặp tin nhắn user/assistant phục vụ hàm `trim_history`), giúp tránh tình trạng lặp dữ liệu và giữ ngữ cảnh chuẩn xác.
  - Bổ sung phụ thuộc `streamlit>=1.30.0` vào `starter_v0/requirements.txt`.

- **Phát triển Module Adapter An toàn (`starter_v0/ui_adapter.py`):**
  - Nhằm tránh rủi ro xung đột trạng thái khi nhiều phiên Streamlit cùng chạy và bảo vệ mã nguồn chung, tôi đã thay thế hoàn toàn giải pháp monkey-patching hàm toàn cục `chat.execute_tool_call` bằng module adapter trung gian.
  - Hàm `safe_execute_tool_call()` chặn đứng việc thực thi công cụ `send` ở mức runtime trên UI, trả về thông báo an toàn rõ ràng ngay cả khi mô hình truyền `confirmed=True`.
  - Hàm `safe_run_model_tool_loop()` bọc vòng lặp xử lý mô hình và công cụ, kế thừa trực tiếp các hàm thuần túy (pure helpers) từ `chat.py` mà không gây bất kỳ tác dụng phụ nào tới hệ thống benchmark của nhóm.

- **Xử lý Lỗi Nhà cung cấp (`sanitize_provider_error`):**
  - Trong quá trình kiểm thử với Gemini API thật, tôi ghi nhận trường hợp API bị quá tải và trả về lỗi `ServerError: 503 UNAVAILABLE`. Tôi đã xây dựng hàm `sanitize_provider_error()` để phân tích chuỗi lỗi, chuyển đổi thành thông báo tiếng Việt lịch sự hướng dẫn người dùng thử lại sau ít phút.
  - Lượt gặp lỗi không bị ghi vào `llm_history`, nhờ đó bảo toàn toàn bộ ngữ cảnh trước đó khi người dùng bấm gửi lại câu hỏi.

- **Lưu vết Transcript Tự động:**
  - Tôi triển khai các hàm `create_session_transcript()` và `append_transcript_turn()` để đồng bộ trạng thái hội thoại từ Streamlit vào cấu trúc transcript chuẩn.
  - Mỗi phiên làm việc trên giao diện tự động khởi tạo và cập nhật file JSON trong thư mục `starter_v0/transcripts/`, ghi nhận đầy đủ `transcript_id`, `provider`, `model`, `artifact_version`, `prompt_hash`, `tools_hash`, chi tiết các `tool_events` và trạng thái từng lượt đàm thoại.

- **Xử lý lỗi import khi nạp lại giao diện Streamlit:**
  - Trong quá trình phát triển, khi khởi động lại giao diện Streamlit đã phát sinh lỗi `ImportError: cannot import name 'sanitize_provider_error' from 'ui_adapter'`. Lỗi này cho thấy tại thời điểm import ở runtime, hàm `sanitize_provider_error` chưa sẵn sàng trong module được nạp.
  - Về mặt kỹ thuật, thuộc tính `__all__` trong Python chủ yếu điều khiển wildcard import (`from module import *`) chứ không giải quyết trực tiếp lỗi import tường minh. Trong quá trình điều tra và khắc phục sự cố, việc bộ nhớ đệm module (`sys.modules`) bị cũ là một giả thuyết khả dĩ. Tôi đã bổ sung khai báo `__all__` để chuẩn hóa danh mục xuất khẩu, chuẩn hóa đường dẫn tìm kiếm `sys.path`, và đưa vào cơ chế nạp lại mô-đun chủ động (`importlib.reload(ui_adapter)`) trong `app.py`. Sau các bước này, các lệnh kiểm tra import đều vượt qua thành công.

---

## 4. Bằng chứng

- **File/commit/PR:**
  - Nhánh Git công tác: `feat/ui-stream-demo`
  - Các file mã nguồn chính do tôi tạo và cập nhật:
    - [`starter_v0/app.py`](../../starter_v0/app.py): Ứng dụng giao diện Web Streamlit.
    - [`starter_v0/ui_adapter.py`](../../starter_v0/ui_adapter.py): Module adapter an toàn, xử lý lỗi và lưu vết transcript.
    - [`starter_v0/requirements.txt`](../../starter_v0/requirements.txt): Cập nhật gói phụ thuộc Streamlit.
  - Dữ liệu thực nghiệm transcript:
    - [`starter_v0/transcripts/v0_gemini_20261111T001248833127.transcript.json`](../../starter_v0/transcripts/v0_gemini_20261111T001248833127.transcript.json): Phiên đàm thoại thực tế 3 lượt với Gemini (`gemini-3.5-flash-lite`), ghi nhận lượt 1 gọi `papers` và `format`, lượt 2 gặp lỗi HTTP 503 được bắt an toàn, lượt 3 gọi `lookup`.
    - [`starter_v0/transcripts/v0_gemini_20261111T004018512852.transcript.json`](../../starter_v0/transcripts/v0_gemini_20261111T004018512852.transcript.json): Phiên đàm thoại thực tế 2 lượt với Gemini, ghi nhận lượt 1 gọi `papers`, lượt 2 gọi `papers` và `lookup`.

- **AI/công cụ đã dùng và cách tự kiểm tra kết quả:**
  - *ChatGPT:* Hỗ trợ rà soát yêu cầu bài lab, thảo luận hướng tiếp cận khi triển khai, phân tích lỗi phát sinh và kiểm tra tính nhất quán của các báo cáo.
  - *Phương pháp tôi tự kiểm tra:* Tôi đã tự kiểm tra và đánh giá lại các kết quả mà AI đưa ra thông qua các lệnh terminal, kiểm thử giả lập (mock tests), tương tác trực tiếp trên giao diện Streamlit và kiểm tra các file transcript thực tế.

---

## 5. Tự đánh giá

### 5.1. Điểm mạnh kỹ thuật
- **Kiến trúc an toàn và cô lập:** Việc chủ động loại bỏ monkey-patching để chuyển sang module UI Adapter chuyên biệt giúp ứng dụng Web vừa kiểm soát được các công cụ có tác dụng phụ, vừa bảo vệ tính nguyên vẹn của mã nguồn chung để đồng đội chạy benchmark không bị ảnh hưởng.
- **Xử lý sự cố mạng thực tế:** Việc phân loại và chuẩn hóa lỗi HTTP 503 giúp giao diện duy trì trải nghiệm liền mạch, không làm mất lịch sử trò chuyện khi nhà cung cấp mô hình gặp sự cố quá tải tạm thời.
- **Dữ liệu minh bạch:** Mọi tương tác trên giao diện đều được ghi vết đầy đủ vào file JSON với mã băm artifact tương ứng, bảo đảm tính xác thực theo yêu cầu của bài lab.

### 5.2. Hạn chế và hướng hoàn thiện
- Trong các phiên thử nghiệm thực tế với mô hình thật trên baseline v0, công cụ `clarify` chưa được mô hình kích hoạt trong tương tác trực tiếp (mới chỉ được kiểm chứng qua mock unit test) do System Prompt v0 còn nhiều chỉ dẫn xấu. Tôi cần phối hợp kiểm thử lại trên UI khi Thành viên 1 hoàn thiện bản prompt v3.
- Kết nối Cloudflare Tunnel chưa được khởi chạy trong nhánh công tác này; cần chuẩn bị sẵn sàng lệnh khởi chạy để kích hoạt khi nhóm thực hiện demo trực tiếp.
- Qua bài lab, tôi hiểu rõ hơn cách một AI Agent kết hợp mô hình ngôn ngữ với các công cụ bên ngoài và tầm quan trọng của việc kiểm tra từng bước thực thi. Khó khăn lớn nhất khi tích hợp giao diện là xử lý lỗi từ API và duy trì ngữ cảnh hội thoại, từ đó tôi rút ra kinh nghiệm cần kiểm thử cả những trường hợp lỗi thay vì chỉ kiểm tra khi hệ thống hoạt động bình thường.
