import requests, bs4, re, os
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

from config import CONFIG
from logs.log import logger

LIST_PRODUCT_PATH = CONFIG.get("LIST_PRODUCT_PATH")
JSON_PATH = CONFIG.get("JSON_PATH")

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

def get_succeeded_product_ids():
    succeeded = {}
    # TH: chạy lần đầu
    if not os.path.exists(JSON_PATH):
        return succeeded
    
    # Xử lý file json
    for filename in os.listdir(JSON_PATH):
        if filename.endswith(".json"):
            try:
                batch_index = int(filename.split(".")[0])
            except ValueError:
                continue
            filepath = os.path.join(JSON_PATH, filename)
            # Nếu file rỗng thì bỏ qua
            if os.path.getsize(filepath) == 0:
                continue
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        for item in data:
                            if isinstance(item, dict) and "id" in item:
                                succeeded[str(item["id"])] = batch_index
            except Exception as e:
                logger.warning(f"Không thể đọc file {filename}: {e}")
    return succeeded

def load_all_products():
    products = []
    if not os.path.exists(LIST_PRODUCT_PATH):
        logger.error(f"File danh sách sản phẩm không tồn tại: {LIST_PRODUCT_PATH}")
        return products
    with open(LIST_PRODUCT_PATH, "r", encoding="utf-8") as f:
        next(f) # Bỏ qua header
        for line in f:
            product_id = line.strip()
            if product_id:
                products.append(product_id)
    return products

if __name__ == "__main__":
    # Đảm bảo thư mục lưu JSON tồn tại
    os.makedirs(JSON_PATH, exist_ok=True)
    
    # 1. Lấy danh sách ID đã xử lý thành công
    succeeded = get_succeeded_product_ids()
    if succeeded:
        logger.info(
            f"Phát hiện {len(succeeded)} sản phẩm đã xử lý thành công từ lượt chạy trước. Tiến hành chạy tiếp (Resume)."
        )
        logger.info(
            "Nếu bạn muốn chạy lại hoàn toàn từ đầu, hãy xóa các file JSON trong thư mục data/json/."
        )
    else:
        logger.info("Không phát hiện dữ liệu cũ hoặc bắt đầu lượt chạy mới hoàn toàn từ đầu.")

    # 2. Đọc toàn bộ sản phẩm từ file CSV đầu vào
    all_products = load_all_products()
    total_products = len(all_products)
    logger.info(f"Tổng số sản phẩm từ file CSV: {total_products}")
    
    # 3. Phân nhóm sản phẩm theo batch_index gốc và xác định các ID chưa xử lý
    batches_to_process = {}
    for i, product_id in enumerate(all_products):
        batch_index = i // BATCH_SIZE + 1
        
        # Nếu sản phẩm chưa được xử lý thành công trước đó
        if product_id not in succeeded:
            if batch_index not in batches_to_process:
                batches_to_process[batch_index] = []
            batches_to_process[batch_index].append(product_id)
            
    # 4. Duyệt qua và xử lý các batch cần cập nhật
    total_batches = (total_products + BATCH_SIZE - 1) // BATCH_SIZE
    logger.info(f"Cần xử lý/cập nhật {len(batches_to_process)}/{total_batches} batch.")
    
    for batch_index in sorted(batches_to_process.keys()):
        pending_batch = batches_to_process[batch_index]
        logger.info(
            f"Batch {batch_index} có {len(pending_batch)}/{BATCH_SIZE} sản phẩm cần xử lý."
        )
        
        # Gọi API cho các sản phẩm chưa cào trong batch này
        new_results = process_batch(pending_batch, batch_index)
        
        # Đọc dữ liệu cũ của file batch_index.json (nếu có) để thực hiện gộp
        existing_results = []
        filepath = os.path.join(JSON_PATH, f"{batch_index}.json")
        if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    existing_results = json.load(f)
                    if not isinstance(existing_results, list):
                        existing_results = []
            except Exception as e:
                logger.warning(
                    f"Lỗi khi đọc file cũ {filepath} để gộp: {e}. Sẽ ghi đè file mới."
                )
                
        # Gộp dữ liệu cũ và dữ liệu mới
        # Dùng dict để tránh trùng lặp id
        merged_dict = {
            str(item["id"]): item 
            for item in existing_results 
            if isinstance(item, dict) and "id" in item
        }
        for item in new_results:
            if isinstance(item, dict) and "id" in item:
                merged_dict[str(item["id"])] = item
                
        merged_results = list(merged_dict.values())
        
        # Ghi lại file json
        load_json(merged_results, batch_index)
        
    logger.info("Hoàn thành xử lý toàn bộ dữ liệu.")