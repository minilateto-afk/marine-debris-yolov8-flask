# 匯入 os，用來建立資料夾與處理檔案路徑
import os

# 匯入 uuid，用來產生不重複檔名
import uuid

# 匯入 Flask 相關功能
from flask import Flask, render_template, request, redirect, url_for, flash, send_file

# 匯入 secure_filename，避免上傳檔案名稱有危險字元
from werkzeug.utils import secure_filename

# 匯入專案設定
from config import Config

# 匯入 YOLO 偵測函式
from utils.detector import run_detection

# 匯入統計相關函式
from utils.statistics import (
    append_detection_records,
    get_overall_stats,
    load_summary_data,
    load_detection_data,
    parse_class_counts,
    ensure_csv_files
)

# 匯入圖表產生函式
from utils.chart import generate_all_charts


# 建立 Flask app
app = Flask(__name__)

# 設定 secret key，用於 flash 訊息
app.secret_key = "marine-debris-demo-secret-key"

# 將 config.py 中的設定載入 Flask app
app.config.from_object(Config)


def ensure_project_folders():
    # 建立上傳圖片資料夾
    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)

    # 建立偵測後圖片資料夾
    os.makedirs(Config.OUTPUT_FOLDER, exist_ok=True)

    # 建立統計圖表資料夾
    os.makedirs(Config.CHART_FOLDER, exist_ok=True)

    # 建立 CSV 結果資料夾
    os.makedirs(Config.RESULT_FOLDER, exist_ok=True)

    # 建立 CSV 檔案
    ensure_csv_files()


def allowed_file(filename):
    # 確認檔名中有副檔名
    if "." not in filename:
        return False

    # 取得副檔名並轉成小寫
    ext = filename.rsplit(".", 1)[1].lower()

    # 檢查副檔名是否在允許清單中
    return ext in Config.ALLOWED_EXTENSIONS


@app.route("/")
def index():
    # 顯示首頁與圖片上傳表單
    return render_template("index.html")


@app.route("/detect", methods=["POST"])
def detect():
    # 檢查表單中是否有 file 欄位
    if "file" not in request.files:
        flash("沒有收到圖片檔案，請重新選擇圖片。")
        return redirect(url_for("index"))

    # 取得使用者上傳的檔案
    file = request.files["file"]

    # 如果使用者沒有選檔案
    if file.filename == "":
        flash("尚未選擇圖片，請先選擇一張 JPG 或 PNG 圖片。")
        return redirect(url_for("index"))

    # 檢查檔案格式是否允許
    if not allowed_file(file.filename):
        flash("檔案格式不支援，請上傳 JPG、JPEG 或 PNG 圖片。")
        return redirect(url_for("index"))

    # 使用 secure_filename 清理檔名
    original_filename = secure_filename(file.filename)

    # 取得副檔名
    ext = original_filename.rsplit(".", 1)[1].lower()

    # 產生不重複檔名，避免不同使用者上傳同名檔案互相覆蓋
    unique_name = f"{uuid.uuid4().hex}.{ext}"

    # 設定原始圖片儲存路徑
    upload_path = os.path.join(Config.UPLOAD_FOLDER, unique_name)

    # 儲存使用者上傳的圖片
    file.save(upload_path)

    # 設定偵測後圖片檔名
    output_name = f"detected_{unique_name}"

    # 設定偵測後圖片儲存路徑
    output_path = os.path.join(Config.OUTPUT_FOLDER, output_name)

    try:
        # 執行 YOLOv8 偵測
        detections = run_detection(upload_path, output_path)

        # 將偵測結果寫入 CSV，並取得該圖片摘要
        summary = append_detection_records(
            image_name=unique_name,
            output_name=output_name,
            detections=detections
        )

        # 重新產生 Dashboard 圖表
        generate_all_charts()

    except Exception as e:
        # 如果偵測過程出錯，顯示錯誤訊息
        flash(f"偵測失敗：{str(e)}")
        return redirect(url_for("index"))

    # 統計各類別數量，方便結果頁顯示
    class_counts = parse_class_counts(summary["class_counts_json"])

    # 產生原始圖片網址
    upload_url = url_for("static", filename=f"uploads/{unique_name}")

    # 產生偵測後圖片網址
    output_url = url_for("static", filename=f"outputs/{output_name}")

    # 顯示偵測結果頁
    return render_template(
        "result.html",
        upload_url=upload_url,
        output_url=output_url,
        image_name=unique_name,
        detections=detections,
        summary=summary,
        class_counts=class_counts
    )


@app.route("/dashboard")
def dashboard():
    # 每次進入 Dashboard 都重新產生圖表
    generate_all_charts()

    # 取得整體統計資料
    stats = get_overall_stats()

    # 讀取摘要資料
    summary_df = load_summary_data()

    # 取最近 10 筆分析紀錄
    if summary_df.empty:
        recent_records = []
    else:
        recent_records = summary_df.tail(10).iloc[::-1].to_dict(orient="records")

    # 顯示 Dashboard 頁面
    return render_template(
        "dashboard.html",
        stats=stats,
        recent_records=recent_records
    )


@app.route("/about")
def about():
    # 顯示專題說明頁
    return render_template("about.html")


@app.route("/download/detections")
def download_detections():
    # 確保 CSV 檔案存在
    ensure_csv_files()

    # 下載偵測框詳細紀錄 CSV
    return send_file(Config.DETECTION_CSV, as_attachment=True)


@app.route("/download/summary")
def download_summary():
    # 確保 CSV 檔案存在
    ensure_csv_files()

    # 下載每張圖片摘要 CSV
    return send_file(Config.SUMMARY_CSV, as_attachment=True)


# 如果直接執行 app.py，就啟動 Flask
if __name__ == "__main__":
    # 啟動前先建立必要資料夾
    ensure_project_folders()

    # 啟動 Flask 網站
    app.run(host="0.0.0.0", port=5000, debug=True)