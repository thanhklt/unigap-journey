import os
import yaml

# Xác định đường dẫn tuyệt đối tới file config.yml trong cùng thư mục với file settings.py
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "config.yml")

with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    CONFIG = yaml.safe_load(f)