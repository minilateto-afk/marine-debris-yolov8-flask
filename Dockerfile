# 使用 Python 3.10 作為基礎環境
FROM python:3.10-slim

# 設定容器內的工作資料夾
WORKDIR /app

# 安裝 OpenCV / matplotlib 可能需要的系統套件
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# 複製 requirements.txt 到容器內
COPY requirements.txt .

# 安裝 Python 套件
RUN pip install --no-cache-dir -r requirements.txt

# 複製整個專案到容器內
COPY . .

# 開放 Flask 預設使用的 5000 port
EXPOSE 5000

# 設定 Flask 執行環境
ENV FLASK_APP=app.py
ENV FLASK_ENV=development
ENV PYTHONUNBUFFERED=1

# 啟動 Flask 網站
CMD ["python", "app.py"]