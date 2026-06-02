# marine-debris-yolov8-flask
# 基於 YOLOv8 之海洋廢棄物影像偵測與分類統計系統

<!-- 專題摘要 -->
本專題以海洋廢棄物影像為分析對象，整合 Flask 網頁介面、YOLOv8 物件偵測、OpenCV 影像標註、Pandas 資料整理與 Matplotlib 圖表視覺化，建立一套可進行圖片上傳、AI 偵測、分類統計與結果展示的影像分析系統。

<!-- 系統功能摘要 -->
使用者可上傳海洋廢棄物影像，系統會透過 YOLOv8 進行物件偵測，並在圖片中標示偵測框、類別與信心分數。偵測結果會被整理成 CSV 紀錄，並於 Dashboard 中呈現累積分析結果，包括已分析圖片數、累積偵測物件數、常見類別、平均信心分數與相關視覺化圖表。

<!-- 模型狀態說明 -->
目前版本已完成完整系統流程。若尚未放入自訂訓練模型 `models/best.pt`，系統會先使用 YOLOv8 預訓練模型進行流程測試；後續可使用海洋廢棄物標註資料集訓練專用模型，以提升實際海洋廢棄物影像中的辨識準確度。

---

## 一、專題動機

<!-- 動機說明 -->
海洋廢棄物會影響海岸環境、生態系統與海洋資源管理。傳統影像判讀多仰賴人工觀察，不僅耗費時間，也較難快速整理成可分析的數據資料。因此，本專題嘗試以資訊工程方法，將海洋廢棄物影像轉換為可標註、可統計與可視覺化的資料。

<!-- 資工應用說明 -->
本系統以 YOLOv8 物件偵測為核心，結合 Flask 網頁介面、OpenCV 影像處理、Pandas 資料整理與 Matplotlib 圖表視覺化，建立一套可上傳圖片、顯示偵測結果、紀錄分析資料並呈現統計儀表板的海洋廢棄物影像分析系統。

---

## 二、使用技術

<!-- 後端框架 -->
- Python

<!-- 網頁後端 -->
- Flask

<!-- 物件偵測模型 -->
- YOLOv8

<!-- 影像處理與畫框 -->
- OpenCV

<!-- 資料整理與 CSV 輸出 -->
- Pandas

<!-- 視覺化圖表 -->
- Matplotlib

<!-- 容器化部署 -->
- Docker

<!-- 雲端開發環境 -->
- GitHub Codespaces

---

## 三、系統功能

<!-- 圖片上傳 -->
1. 使用者可上傳 JPG、JPEG、PNG 格式圖片。

<!-- 模型推論 -->
2. 系統使用 YOLOv8 進行物件偵測與類別判斷。

<!-- 影像標註 -->
3. 系統透過 OpenCV 將偵測框、類別名稱與信心分數標示於圖片上。

<!-- 詳細紀錄 -->
4. 系統將每個偵測框的圖片名稱、類別、信心分數與座標資訊寫入 `detections.csv`。

<!-- 摘要紀錄 -->
5. 系統將每張圖片的總偵測數量、平均信心分數與類別統計寫入 `summary.csv`。

<!-- 統計儀表板 -->
6. Dashboard 會呈現已分析圖片數、累積偵測物件數、最常見類別與平均信心分數。

<!-- 視覺化圖表 -->
7. 系統會產生分類數量圖、每張圖片偵測數量圖與信心分數分布圖。

---

## 四、專案架構

```text
marine-debris-yolov8-flask/
│
├── app.py                         # Flask 主程式，負責網站路由與圖片上傳
├── config.py                      # 專案設定，例如模型路徑、資料夾路徑
├── requirements.txt               # Python 套件清單
├── Dockerfile                     # Docker 容器環境設定
├── docker-compose.yml             # Docker Compose 啟動設定
├── README.md                      # 專題說明與執行方式
├── .gitignore                     # Git 忽略檔案設定
│
├── models/
│   ├── README.md                  # 說明模型來源與使用方式
│   └── best.pt                    # YOLOv8 自訂模型權重，正式版放置於此
│
├── data/
│   ├── raw/
│   │   └── sample_images/         # 原始測試圖片
│   ├── processed/                 # 整理後資料或訓練資料
│   └── results/
│       ├── detections.csv         # 每個偵測框的詳細紀錄
│       └── summary.csv            # 每張圖片的統計摘要
│
├── utils/
│   ├── __init__.py                # 讓 utils 成為 Python 模組
│   ├── detector.py                # YOLOv8 偵測與 OpenCV 畫框
│   ├── statistics.py              # CSV 紀錄與統計
│   └── chart.py                   # Matplotlib 圖表產生
│
├── static/
│   ├── css/
│   │   └── style.css              # 網頁樣式
│   ├── uploads/                   # 使用者上傳的原始圖片
│   ├── outputs/                   # 偵測後畫框圖片
│   └── charts/                    # 統計圖表圖片
│
└── templates/
    ├── base.html                  # 共用版型
    ├── index.html                 # 首頁與上傳頁
    ├── result.html                # 單張圖片偵測結果頁
    ├── dashboard.html             # 統計圖表頁
    └── about.html                 # 專題介紹頁