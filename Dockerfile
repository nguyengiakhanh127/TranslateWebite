FROM python:3.10-slim

# 1. Cài đặt Tesseract OCR (Vẫn cần cho tính năng dịch ảnh)
# Không cần cài libmysqlclient-dev nữa -> Build nhanh hơn
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libtesseract-dev \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

# 2. Thiết lập thư mục
WORKDIR /app

# 3. Cài thư viện Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copy code
COPY . .

# 5. Collectstatic
RUN python manage.py collectstatic --noinput

# 6. Chạy Server
EXPOSE 10000
CMD ["gunicorn", "maProject.wsgi:application", "--bind", "0.0.0.0:10000"]