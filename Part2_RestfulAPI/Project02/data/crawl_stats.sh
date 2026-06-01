#!/bin/bash

# Xác định thư mục của script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Cấu hình đường dẫn thư mục
JSON_DIR="$SCRIPT_DIR/json"
SEED_DIR="$SCRIPT_DIR/seed"

total_attempted=0
total_successful=0

# Đảm bảo các thư mục tồn tại
if [ ! -d "$JSON_DIR" ] || [ ! -d "$SEED_DIR" ]; then
    echo "Lỗi: Không tìm thấy thư mục json/ hoặc seed/ trong data/"
    exit 1
fi

echo "============================================="
echo "        THỐNG KÊ TIẾN TRÌNH CÀO DỮ LIỆU"
echo "============================================="
echo "Đang xử lý dữ liệu từ các lô..."

# Duyệt qua các file json đã cào thành công trong json/
for json_file in "$JSON_DIR"/*.json; do
    # Bỏ qua nếu không tìm thấy file nào khớp
    [ -e "$json_file" ] || continue
    
    # Lấy tên file và số lô (ví dụ: 1.json -> 1)
    filename=$(basename "$json_file")
    batch_num="${filename%.json}"
    
    # Đường dẫn file seed tương ứng
    seed_file="$SEED_DIR/${batch_num}.csv"
    
    if [ -f "$seed_file" ]; then
        # Đếm số lượng product ID hợp lệ trong file seed (tổng số sản phẩm cần cào của lô)
        batch_total=$(grep -E -c "^[0-9]+$" "$seed_file" 2>/dev/null || echo 0)
        
        # Đếm số lượng sản phẩm cào thành công (số lượng "id": trong file json)
        batch_success=$(grep -c '"id":' "$json_file" 2>/dev/null || echo 0)
        
        total_attempted=$((total_attempted + batch_total))
        total_successful=$((total_successful + batch_success))
    fi
done

# Tính toán số lượng thất bại
total_failed=$((total_attempted - total_successful))

# Tránh chia cho 0 nếu chưa có dữ liệu nào được cào
if [ "$total_attempted" -eq 0 ]; then
    success_rate="0.00"
    fail_rate="0.00"
else
    success_rate=$(awk -v s="$total_successful" -v t="$total_attempted" 'BEGIN { printf "%.2f", (s/t)*100 }')
    fail_rate=$(awk -v f="$total_failed" -v t="$total_attempted" 'BEGIN { printf "%.2f", (f/t)*100 }')
fi

echo "---------------------------------------------"
echo "Tổng số dữ liệu đã cào (attempted) : $total_attempted sản phẩm"
echo "Số lượng thành công (success)      : $total_successful sản phẩm"
echo "Số lượng thất bại (fail)           : $total_failed sản phẩm"
echo "---------------------------------------------"
echo "Tỷ lệ thành công                   : ${success_rate}%"
echo "Tỷ lệ thất bại                     : ${fail_rate}%"
echo "============================================="
