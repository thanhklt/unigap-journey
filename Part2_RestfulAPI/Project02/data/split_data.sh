#!/bin/bash

# Đảm bảo thư mục seed tồn tại
SEED_DIR="seed"
mkdir -p "$SEED_DIR"

# File nguồn theo thứ tự
FILES=(
  "products-0-200000.csv"
  "products-200001-400000.csv"
  "products-400001-600000.csv"
)

echo "Bắt đầu chia dữ liệu bằng awk..."

# Dùng awk để gộp dữ liệu từ các file, bỏ qua header của mỗi file (FNR > 1), 
# và ghi thành các file lô nhỏ 1000 dòng bắt đầu từ 1.csv
awk '
  BEGIN {
    file_idx = 1
    line_count = 0
    seed_dir = "seed"
  }
  FNR > 1 {
    out_file = seed_dir "/" file_idx ".csv"
    print $0 > out_file
    line_count++
    if (line_count == 1000) {
      close(out_file)
      file_idx++
      line_count = 0
    }
  }
  END {
    if (line_count > 0) {
      close(seed_dir "/" file_idx ".csv")
      print "Lô cuối cùng: " file_idx ".csv chứa " line_count " dòng."
    } else {
      print "Tổng số lô đã tạo: " (file_idx - 1)
    }
  }
' "${FILES[@]}"

echo "Hoàn thành! Đã chia dữ liệu thành các lô trong thư mục: $SEED_DIR"
