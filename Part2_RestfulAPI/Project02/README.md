# Tiki Product Data Crawler

Chương trình cào (crawl) thông tin chi tiết sản phẩm từ API của Tiki dựa trên danh sách Product ID có sẵn. Dự án được tối ưu hiệu năng thông qua lập trình đa luồng (multi-threading) và hỗ trợ cơ chế lưu vết trạng thái (checkpointing) để tiếp tục tiến trình khi gặp sự cố mà không cần chạy lại từ đầu.

---

## 📌 Các Tính Năng Chính

- **Tải dữ liệu song song (Multi-threading):** Sử dụng `ThreadPoolExecutor` để gửi nhiều yêu cầu đồng thời đến Tiki API, giúp tối ưu hóa thời gian xử lý lô lớn sản phẩm.
- **Cơ chế lưu vết và phục hồi (State Recovery):** Theo dõi tiến độ chạy thông qua tệp tin `data/current_status.json`. Nếu chương trình bị ngắt đột ngột, chương trình sẽ tự động nhận diện và tiếp tục từ lô (batch) chưa hoàn thành gần nhất.
- **Trích xuất & làm sạch dữ liệu:** Tự động lọc các trường thông tin cần thiết (`id`, `name`, `url_key`, `price`, `description`), đồng thời làm sạch mã HTML của mô tả sản phẩm bằng thư viện `BeautifulSoup4`.
- **Hệ thống Ghi log chi tiết:** Tách biệt hai loại log chính để tiện theo dõi:
  - `logs/app.log`: Ghi nhận tất cả lịch sử hoạt động (`INFO`, `WARNING`, `ERROR`).
  - `logs/error.log`: Chỉ ghi nhận lỗi nghiêm trọng (`ERROR`, `CRITICAL`), ví dụ: mã lỗi HTTP 404, 500, lỗi kết nối hoặc timeout.

---

## 📂 Cấu Trúc Thư Mục Dự Án

```text
Project02/
├── config/
│   ├── __init__.py
│   ├── config.yml          # Cấu hình tham số hệ thống (API endpoint, workers, keys...)
│   └── settings.py          # Script tải cấu hình YAML
├── data/
│   ├── seed/               # Thư mục chứa các tệp tin CSV mẫu Product ID (ví dụ: 0.csv, 1.csv...)
│   ├── json/               # Thư mục chứa dữ liệu JSON kết quả sau khi cào
│   └── current_status.json # Lưu trữ trạng thái tiến trình chạy (lô hiện tại, thời gian chạy...)
├── logs/
│   ├── log.py              # Cấu hình Logger cho hệ thống
│   ├── app.log             # Nhật ký hoạt động chung của toàn bộ script
│   └── error.log           # Nhật ký các lỗi phát sinh (HTTP 404, 500, timeout...)
├── .venv/                  # Môi trường ảo Python (Virtual Environment)
├── main.py                 # File thực thi chính của chương trình
├── requirements.txt        # Danh sách thư viện phụ thuộc
├── Note.md                 # Ghi chú kỹ thuật & giải pháp tối ưu hóa tiến trình
└── README.md               # Hướng dẫn sử dụng dự án (File này)
```

---

## ⚙️ Cấu Hình (`config/config.yml`)

Bạn có thể dễ dàng thay đổi hành vi của chương trình bằng cách cấu hình tệp `config/config.yml`:

```yaml
# Thư mục lưu trữ log
LOGGING_PATH: "logs"
LOG_APP_PATH: "logs/app.log"
LOG_ERROR_PATH: "logs/error.log"

# Đường dẫn dữ liệu nguồn và đích
LIST_PRODUCT_PATH: "data/products-0-200000.csv"
JSON_PATH: "data/json/"
SEED_DIR: "data/seed/"
STATUS_FILE_PATH: "data/current_status.json"

# Tiki API Endpoint
ENDPOINT: "https://api.tiki.vn/product-detail/api/v1/products/"

# Các trường dữ liệu cần trích xuất từ phản hồi API
KEY_DATA:
  - "id"
  - "name"
  - "url_key"
  - "price"
  - "description"

# Tham số hiệu năng
BATCH_SIZE: 1000   # Kích thước của mỗi lô sản phẩm
MAX_WORKERS: 20    # Số luồng (threads) đồng thời gửi yêu cầu API
```

---

## 🚀 Hướng Dẫn Cài Đặt và Chạy

### 1. Yêu cầu hệ thống
- Máy tính đã cài đặt Python 3.8 trở lên.

### 2. Thiết lập môi trường và cài đặt thư viện
Kích hoạt môi trường ảo Python và cài đặt các thư viện cần thiết:

```bash
# 1. Kích hoạt môi trường ảo (Windows PowerShell)
.venv\Scripts\Activate.ps1

# Hoặc Command Prompt:
# .venv\Scripts\activate.bat

# 2. Cài đặt các thư viện phụ thuộc
pip install -r requirements.txt
```

> Các thư viện chính được sử dụng bao gồm:
> - `requests`: Gửi yêu cầu HTTP đến Tiki API.
> - `beautifulsoup4`: Phân tích cú pháp và làm sạch dữ liệu HTML.
> - `PyYAML`: Đọc cấu hình từ file YAML.

### 3. Thực thi chương trình
Chạy tập lệnh cào dữ liệu:

```bash
python main.py
```

Chương trình sẽ:
1. Đọc trạng thái từ `current_status.json` để biết đã hoàn thành tới lô nào.
2. Quét thư mục `data/seed/` để lấy danh sách các file lô `.csv` còn lại cần xử lý.
3. Tiến hành gọi API song song cho các sản phẩm trong mỗi lô.
4. Ghi kết quả vào `data/json/{batch_index}.json`.
5. Cập nhật tiến độ sau khi hoàn thành mỗi lô.

---

## 🛠️ Xử Lý Lỗi và Sự Cố Thường Gặp

Khi chạy chương trình với hiệu năng cao (`MAX_WORKERS` lớn), bạn có thể gặp một số lỗi được ghi lại trong `logs/error.log`:

1. **Lỗi `WinError 10048` (Only one usage of each socket address is normally permitted):**
   - **Nguyên nhân:** Xảy ra do hệ điều hành cạn kiệt cổng kết nối (socket port) khả dụng khi gửi quá nhiều yêu cầu HTTP liên tục mà socket cũ chưa kịp giải phóng khỏi trạng thái `TIME_WAIT`.
   - **Khắc phục:** Giảm số lượng `MAX_WORKERS` trong file `config.yml` xuống thấp hơn (ví dụ: 10 hoặc 15) hoặc tăng thời gian trễ giữa các lượt gửi.

2. **Lỗi `Read timed out` (Connection Timeout):**
   - **Nguyên nhân:** Tiki API phản hồi chậm hơn 10 giây hoặc do nghẽn mạng.
   - **Khắc phục:** Kiểm tra đường truyền Internet hoặc điều chỉnh tham số `timeout` trong hàm `fetch_product` của `main.py`.

3. **Status code `404` / `500`:**
   - **Mã 404 (Not Found):** Sản phẩm không tồn tại hoặc đã bị xóa khỏi hệ thống Tiki. Đây là lỗi bình thường khi cào dữ liệu danh sách lớn.
   - **Mã 500 (Internal Server Error):** Lỗi từ phía máy chủ Tiki.

---

## 📈 Giám Sát Tiến Trình

Bạn có thể thống kê nhanh trạng thái thông qua script có sẵn:

```bash
bash data/crawl_stats.sh
```

Kết quả hiển thị tương tự:
```text
=============================================
        THỐNG KÊ TIẾN TRÌNH CÀO DỮ LIỆU      
=============================================
Đang xử lý dữ liệu từ các lô...
---------------------------------------------
Tổng số dữ liệu đã cào (attempted) : 240000 sản phẩm
Số lượng thành công (success)      : 152933 sản phẩm
Số lượng thất bại (fail)           : 87067 sản phẩm 
---------------------------------------------       
Tỷ lệ thành công                   : 63.72%
Tỷ lệ thất bại                     : 36.28%
=============================================
```

Để tìm kiếm nhanh tất cả các dòng lỗi nghiêm trọng **ngoài lỗi 404** trong log lỗi, sử dụng câu lệnh:
```bash
egrep -v '404' logs/error.log
```
