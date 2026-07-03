# Sử dụng Python base image nhẹ và chính thức
FROM python:3.10-slim

# Thiết lập các biến môi trường hữu ích
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Thiết lập thư mục làm việc trong container
WORKDIR /app

# Copy tệp requirements trước để tận dụng Docker cache cho dependencies
COPY requirements.txt .

# Cài đặt dependencies (lxml và các thư viện khác có pre-built wheels cho Linux)
RUN pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ mã nguồn của dự án vào container
COPY . .

# Mặc định chạy main.py khi container khởi chạy
CMD ["python", "main.py"]
