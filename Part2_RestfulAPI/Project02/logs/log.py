import os
import logging
import sys
from config import CONFIG

# Đảm bảo terminal in được tiếng Việt UTF-8 không bị lỗi UnicodeEncodeError trên Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

LOG_APP_PATH = CONFIG.get("LOG_APP_PATH")
LOG_ERROR_PATH = CONFIG.get("LOG_ERROR_PATH")

# Đảm bảo thư mục lưu log tồn tại
if LOG_APP_PATH:
    os.makedirs(os.path.dirname(LOG_APP_PATH), exist_ok=True)
if LOG_ERROR_PATH:
    os.makedirs(os.path.dirname(LOG_ERROR_PATH), exist_ok=True)

# Cấu hình root logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Tránh add nhiều handler nếu file được import nhiều lần
if not logger.handlers:
    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s"
    )

    # File app.log: ghi toàn bộ INFO, WARNING, ERROR
    app_handler = logging.FileHandler(LOG_APP_PATH, encoding="utf-8")
    app_handler.setLevel(logging.INFO)
    app_handler.setFormatter(formatter)

    # File error.log: chỉ ghi ERROR trở lên
    error_handler = logging.FileHandler(LOG_ERROR_PATH, encoding="utf-8")
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)

    # Console: in log trực tiếp ra terminal để theo dõi
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    logger.addHandler(app_handler)
    logger.addHandler(error_handler)
    logger.addHandler(console_handler)
