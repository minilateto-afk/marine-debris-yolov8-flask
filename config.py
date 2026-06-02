# 匯入 os，用來處理資料夾路徑
import os


# Config 類別：集中管理整個專案的設定
class Config:
    # 取得目前專案的根目錄
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))

    # 使用者上傳圖片的資料夾
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")

    # YOLO 偵測後圖片輸出的資料夾
    OUTPUT_FOLDER = os.path.join(BASE_DIR, "static", "outputs")

    # Matplotlib 統計圖表輸出的資料夾
    CHART_FOLDER = os.path.join(BASE_DIR, "static", "charts")

    # CSV 統計結果存放資料夾
    RESULT_FOLDER = os.path.join(BASE_DIR, "data", "results")

    # 自訂 YOLOv8 模型路徑
    # 之後你訓練好海洋廢棄物模型後，把 best.pt 放到 models/best.pt
    CUSTOM_MODEL_PATH = os.path.join(BASE_DIR, "models", "best.pt")

    # 如果還沒有自訂模型，就先用 YOLOv8 nano 預訓練模型做流程測試
    FALLBACK_MODEL_NAME = "yolov8n.pt"

    # 每個偵測框的詳細紀錄 CSV
    DETECTION_CSV = os.path.join(RESULT_FOLDER, "detections.csv")

    # 每張圖片的統計摘要 CSV
    SUMMARY_CSV = os.path.join(RESULT_FOLDER, "summary.csv")

    # 允許上傳的圖片副檔名
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}

    # YOLO 偵測信心分數門檻
    CONFIDENCE_THRESHOLD = 0.25