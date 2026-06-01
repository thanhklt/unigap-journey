import requests, bs4, re, os
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from config import CONFIG
from logs.log import logger

LIST_PRODUCT_PATH = CONFIG.get("LIST_PRODUCT_PATH")
JSON_PATH = CONFIG.get("JSON_PATH")
SEED_DIR = CONFIG.get("SEED_DIR")
STATUS_FILE_PATH = CONFIG.get("STATUS_FILE_PATH")

ENDPOINT = CONFIG.get("ENDPOINT")
KEY_DATA = CONFIG.get("KEY_DATA")
BATCH_SIZE = CONFIG.get("BATCH_SIZE")
MAX_WORKERS = CONFIG.get("MAX_WORKERS")

def fetch_product(product_id):
    try:
        logger.info(f"Đang xử lý product id: {product_id}")
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
            "Referer": "https://tiki.vn/"
        }
        response = requests.get(
            ENDPOINT + product_id,
            headers=headers,
            timeout=10
        )
        if response.status_code != 200:
            logger.error(
                f"Product id {product_id} trả về status code {response.status_code}"
            )
            return None
        data = response.json()
        extracted_data = extract_key_data(data)
        logger.info(f"Xử lý thành công product id: {product_id}")
        return extracted_data
    
    except Exception as e:
        logger.error(f"Xử lý thất bại product id: {product_id} - {e}")
        return None
    
def extract_key_data(json_data):
    json = {}
    for key in KEY_DATA:
        if key == "description":
            soup = bs4.BeautifulSoup(json_data.get(key, ""))
            product_description = soup.get_text()
            product_description = re.sub(r'\s+', ' ', product_description)
            product_description = re.sub(r'[\n]+', '. ', product_description)
            json[key] = product_description.strip(" .")
        else:
            json[key] = json_data.get(key, None)
    return json

def process_batch(batch, batch_index):
    logger.info(f"Bắt đầu xử lý batch {batch_index}, số lượng: {len(batch)}")
    batch_results = []
    
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = []
        for product_id in batch:
            future = executor.submit(fetch_product, product_id) # Giao cho 1 thread gọi API 1 product
            futures.append(future) # Lưu lại future ( đại diện cho 1 job đang hoặc sẽ làm) để sau này lấy kết quả

        for future in as_completed(futures):
            result = future.result()
            if result is not None:
                batch_results.append(result)
        logger.info(
            f"Hoàn thành batch {batch_index}, thành công {len(batch_results)}/{len(batch)}"
        )

    return batch_results

def load_json(results, batch_index):
    with open(JSON_PATH + f"{batch_index}.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=4)

def load_status():
    default_status = {"current_batch": 0, "last_runtime": 0, "last_updated": ""}
    if not os.path.exists(STATUS_FILE_PATH):
        return default_status
    try:
        with open(STATUS_FILE_PATH, "r", encoding="utf-8") as f:
            status = json.load(f)
            if "current_batch" not in status:
                status["current_batch"] = 0
            if "last_runtime" not in status:
                status["last_runtime"] = 0
            return status
    except Exception as e:
        logger.warning(f"Không thể đọc file current_status.json ({e}). Sử dụng giá trị mặc định.")
        return default_status

def save_status(batch_index, elapsed_time):
    last_updated = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    status = {
        "current_batch": batch_index,
        "last_runtime": int(elapsed_time),
        "last_updated": last_updated
    }
    try:
        parent_dir = os.path.dirname(STATUS_FILE_PATH)
        if parent_dir:
            os.makedirs(parent_dir, exist_ok=True)
        with open(STATUS_FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(status, f, ensure_ascii=False, indent=4)
        logger.info(f"Đã cập nhật trạng thái: lô {batch_index}, tổng thời gian chạy tích lũy: {int(elapsed_time)}s")
    except Exception as e:
        logger.error(f"Không thể ghi file trạng thái {STATUS_FILE_PATH}: {e}")

def load_batch_products(batch_index):
    filepath = os.path.join(SEED_DIR, f"{batch_index}.csv")
    products = []
    if not os.path.exists(filepath):
        logger.error(f"File seed cho lô {batch_index} không tồn tại: {filepath}")
        return products
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                product_id = line.strip()
                if product_id:
                    products.append(product_id)
    except Exception as e:
        logger.error(f"Lỗi khi đọc file seed cho lô {batch_index}: {e}")
    return products

if __name__ == "__main__":
    # Đảm bảo các thư mục lưu JSON và seed tồn tại
    os.makedirs(JSON_PATH, exist_ok=True)
    os.makedirs(SEED_DIR, exist_ok=True)
    
    # 1. Đọc trạng thái chạy cũ
    status = load_status()
    current_batch = status.get("current_batch", 0)
    accumulated_time = status.get("last_runtime", 0)
    
    logger.info(f"Bắt đầu script. Trạng thái hiện tại: Lô đã hoàn thành = {current_batch}, Tổng thời gian chạy tích lũy = {accumulated_time}s")
    
    # 2. Quét thư mục seed để tìm danh sách các lô
    if not os.path.exists(SEED_DIR):
        logger.error(f"Thư mục seed không tồn tại: {SEED_DIR}")
        exit(1)
        
    seed_files = os.listdir(SEED_DIR)
    batches = []
    for filename in seed_files:
        if filename.endswith(".csv"):
            try:
                # Lấy số lô từ tên file (ví dụ "79.csv" -> 79)
                batch_num = int(filename.split(".")[0])
                batches.append(batch_num)
            except ValueError:
                continue
                
    if not batches:
        logger.warning(f"Không tìm thấy file seed CSV nào trong thư mục {SEED_DIR}")
        exit(0)
        
    batches.sort()
    max_batch = batches[-1]
    
    # 3. Lọc danh sách các lô chưa xử lý
    pending_batches = [b for b in batches if b > current_batch]
    logger.info(f"Tổng số lô: {len(batches)}. Số lô cần xử lý tiếp: {len(pending_batches)}")
    
    if not pending_batches:
        logger.info("Tất cả các lô đã được xử lý hoàn thành.")
        exit(0)
        
    # Ghi nhận thời gian bắt đầu chạy của phiên này
    start_time = time.time()
    
    # 4. Duyệt xử lý từng lô chưa hoàn thành
    for batch_index in pending_batches:
        logger.info(f"=== Bắt đầu xử lý Lô {batch_index}/{max_batch} ===")
        
        # Load Product ID từ file seed tương ứng
        products = load_batch_products(batch_index)
        if not products:
            logger.warning(f"Lô {batch_index} không có sản phẩm nào để xử lý. Bỏ qua.")
            # Cập nhật trạng thái cho lô rỗng để tránh lặp lại
            elapsed_now = accumulated_time + (time.time() - start_time)
            save_status(batch_index, elapsed_now)
            continue
            
        # Gọi ThreadPoolExecutor để xử lý song song các sản phẩm trong lô
        results = process_batch(products, batch_index)
        
        # Lưu dữ liệu cào về vào data/json/{batch_index}.json
        load_json(results, batch_index)
        
        # Tính toán tổng thời gian đã chạy tích lũy
        elapsed_now = accumulated_time + (time.time() - start_time)
        
        # Lưu trạng thái tiến trình
        save_status(batch_index, elapsed_now)
        logger.info(f"=== Hoàn thành Lô {batch_index} (Đã lưu {len(results)}/{len(products)} sản phẩm thành công) ===")
        
    logger.info("Hoàn thành xử lý toàn bộ dữ liệu.")