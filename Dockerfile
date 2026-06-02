# 使用 Python 3.10 slim 版本作為基礎映像檔
FROM python:3.10-slim

# 設定容器內的工作目錄
WORKDIR /app

# 安裝系統套件
# libgl1：讓 OpenCV 可以正常處理圖片
# libglib2.0-0：OpenCV 常用相依套件
# fonts-noto-cjk：安裝中文字體，避免 Matplotlib 中文變成方框
# fontconfig：讓系統可以更新並辨識字體
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    fonts-noto-cjk \
    fontconfig \
    && fc-cache -fv \
    && rm -rf /var/lib/apt/lists/*

# 複製 requirements.txt 到容器內
COPY requirements.txt .

# 安裝 Python 套件
RUN pip install --no-cache-dir -r requirements.txt

# 複製整個專案到容器內
COPY . .

# 開放 Flask 使用的 5000 port
EXPOSE 5000

# 設定 Flask 主程式
ENV FLASK_APP=app.py

# 設定 Flask 開發模式
ENV FLASK_ENV=development

# 讓 Python 輸出即時顯示在終端機
ENV PYTHONUNBUFFERED=1

# 啟動 Flask 網站
CMD ["python", "app.py"]