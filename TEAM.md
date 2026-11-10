# Team

## Thông tin nhóm

- Tên nhóm:
- Lớp: L3A / L3B
- Repo nhóm: `K5-L3A-DAY03-TenNhom-ResearchAgentToolEval` hoặc `K5-L3B-DAY03-TenNhom-ResearchAgentToolEval` (xem [SUBMISSION.md](SUBMISSION.md))
- URL repo, nhánh nộp, commit chốt:

## Thành viên

| STT | Họ tên | MSSV | Email | GitHub | Vai trò |
| --: | ------ | ---- | ----- | ------ | ------- |
|   1 | Nguyễn Anh Quân | 2A202603950 | anhhquan511@gmail.com | | Log Analyst & Eval Designer |
|   2 |        |      |       |        |         |

## Cá nhân

Mỗi thành viên đồng thời tạo một báo cáo riêng trong `report/` theo dạng:

```text
report/team/MSSV_HoTen.md
```

Ví dụ: `report/team/20241234_NguyenVanAn.md`.

Sao chép mục dưới đây cho từng thành viên.

## NguyenAnhQuan-2A202603950

### Phần việc phụ trách
- Checkpoint: CP1, CP4
- Đầu việc: Đọc run JSON, gán loại lỗi cho case FAIL (B2), đưa giả thuyết cho từng version; viết 10 case eval_group.json (5 single + 5 multi turn), chạy --suite group (B3).

### Đóng góp cụ thể
- Trích xuất dữ liệu run JSON Baseline v0, phân tích phân loại nguyên nhân 7 ca FAIL ở Mục B2.
- Thiết lập giả thuyết cho các vòng tối ưu v1, v2, v3 dựa trên bằng chứng log thật.
- Thiết kế trọn vẹn 10 test cases trong `starter_v0/data/eval_group.json` (5 single-turn + 5 multi-turn) bao quát cả 2 tool mới của nhóm.

### Bằng chứng
- File `starter_v0/data/eval_group.json`
- File `report/team/2A202603950_NguyenAnhQuan.md`
- Commit cá nhân `bde12ba` trên nhánh `feature/CP3`
