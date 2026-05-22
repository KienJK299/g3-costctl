3. Nếu lỡ chạy `clean --apply` trong account dùng chung với team khác, em muốn có thêm:

- xác nhận môi trường (dev/staging/prod)
- summary số lượng resource trước khi xóa
- protected tag cho resource quan trọng
- IAM policy chặn xóa resource production

5. Sang W7 em sẽ tiếp tục giữ các command:

- `list`
- `cost`
- `tag`
- `idle`

vì các command này hữu ích cho việc quản lý và quan sát tài nguyên trên nhiều account.

Khả năng cao sẽ drop `clean` cần cẩn thận hơn trong môi trường production vì đây là command có khả năng gây ảnh hưởng lớn nếu dùng sai.
