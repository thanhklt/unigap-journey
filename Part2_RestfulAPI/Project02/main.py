import requests, bs4, re
import json
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

LIST_PRODUCT_PATH = r"data/products-0-200000.csv"
JSON_PATH = r"data/json/"
LOGGING_PATH = "logging"

ENDPOINT = r"https://api.tiki.vn/product-detail/api/v1/products/"
KEY_DATA = ["id", "name", "url_key", "price", "description"]
BATCH_SIZE = 1000
MAX_WORKERS = 20

# Log setting
logger = logging.getLogger()
logger.setLevel(logging.INFO)

formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(message)s"
)

# File app.log: ghi toàn bộ INFO, WARNING, ERROR
app_handler = logging.FileHandler("log/app.log", encoding="utf-8")
app_handler.setLevel(logging.INFO)
app_handler.setFormatter(formatter)

# File error.log: chỉ ghi ERROR trở lên
error_handler = logging.FileHandler("log/error.log", encoding="utf-8")
error_handler.setLevel(logging.ERROR)
error_handler.setFormatter(formatter)

logger.addHandler(app_handler)
logger.addHandler(error_handler)

def fetch_product(product_id):
    try:
        logging.info(f"Đang xử lý product id: {product_id}")
        response = requests.get(
            ENDPOINT + product_id,
            timeout=10
        )
        if response.status_code != 200:
            logging.error(
                f"Product id {product_id} trả về status code {response.status_code}"
            )
            return None
        data = response.json()
        extracted_data = extract_key_data(data)
        logging.info(f"Xử lý thành công product id: {product_id}")
        return extracted_data
    
    except Exception as e:
        logging.error(f"Xử lý thất bại product id: {product_id} - {e}")
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
    logging.info(f"Bắt đầu xử lý batch {batch_index}, số lượng: {len(batch)}")
    batch_results = []
    
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = []
        for product_id in batch:
            future = executor.submit(fetch_product, product_id) # Giao cho 1 thread xử lý product_id
            futures.append(future)

        for future in as_completed(futures):
            result = future.result()
            if result is not None:
                batch_results.append(result)
        logging.info(
            f"Hoàn thành batch {batch_index}, thành công {len(batch_results)}/{len(batch)}"
        )

    return batch_results

def load_json(results, batch_index):
    with open(JSON_PATH + f"{batch_index}.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=4)

with open(LIST_PRODUCT_PATH, "r") as f:
    next(f) # Bo qua header
    batch = []
    batch_index = 1

    for i,line in enumerate(f):
        product_id = line.strip()
        batch.append(product_id)

        if len(batch) == BATCH_SIZE:
            results = process_batch(batch, batch_index)
            load_json(results, batch_index)
            # Reset batch
            batch = []
            batch_index += 1

    # Xử lý batch cuối nếu còn dư dưới 1000 product
    if batch:
        results = process_batch(batch, batch_index)
        load_json(results, batch_index)

    logging.info("Hoàn thành xử lý")