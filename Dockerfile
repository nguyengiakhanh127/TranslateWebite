# Sử dụng Linux nhẹ
FROM python:3.10-slim

# 1. Cài đặt Tesseract OCR và các thư viện hệ thống
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libtesseract-dev \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

# 2. Thiết lập thư mục làm việc
WORKDIR /app

# 3. Cài đặt thư viện Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copy code vào
COPY . .

# 5. Thu thập file tĩnh (CSS/JS)
RUN python manage.py collectstatic --noinput

# 6. Mở cổng 10000 (Mặc định của Render)
EXPOSE 10000

# 7. Lệnh chạy server
# Thay 'maProject' bằng tên thư mục chứa settings.py của bạn
CMD ["gunicorn", "maProject.wsgi:application", "--bind", "0.0.0.0:10000"]