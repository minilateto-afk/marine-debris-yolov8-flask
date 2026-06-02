# 匯入 os，用來檢查檔案與資料夾
import os

# 匯入 json，用來把類別數量字典存成文字
import json

# 匯入 pandas，用來整理 CSV 資料
import pandas as pd

# 匯入 datetime，用來記錄偵測時間
from datetime import datetime

# 匯入 Config 設定
from config import Config


# 每個偵測框詳細紀錄的欄位
DETECTION_COLUMNS = [
    "image_name",
    "output_name",
    "class_name",
    "confidence",
    "x1",
    "y1",
    "x2",
    "y2",
    "created_at"
]


# 每張圖片摘要統計的欄位
SUMMARY_COLUMNS = [
    "image_name",
    "output_name",
    "total_count",
    "avg_confidence",
    "class_counts_json",
    "created_at"
]


def ensure_csv_files():
    # 確保結果資料夾存在
    os.makedirs(Config.RESULT_FOLDER, exist_ok=True)

    # 如果 detections.csv 不存在，或檔案大小為 0，重新建立含欄位的空 CSV
    if (not os.path.exists(Config.DETECTION_CSV)) or os.path.getsize(Config.DETECTION_CSV) == 0:
        pd.DataFrame(columns=DETECTION_COLUMNS).to_csv(
            Config.DETECTION_CSV,
            index=False,
            encoding="utf-8-sig"
        )

    # 如果 summary.csv 不存在，或檔案大小為 0，重新建立含欄位的空 CSV
    if (not os.path.exists(Config.SUMMARY_CSV)) or os.path.getsize(Config.SUMMARY_CSV) == 0:
        pd.DataFrame(columns=SUMMARY_COLUMNS).to_csv(
            Config.SUMMARY_CSV,
            index=False,
            encoding="utf-8-sig"
        )


def safe_read_csv(file_path, columns):
    # 先確保 CSV 檔案存在且不是空檔
    ensure_csv_files()

    # 如果檔案不存在，直接回傳指定欄位的空 DataFrame
    if not os.path.exists(file_path):
        return pd.DataFrame(columns=columns)

    # 如果檔案存在但大小為 0，也回傳空 DataFrame
    if os.path.getsize(file_path) == 0:
        return pd.DataFrame(columns=columns)

    # 嘗試讀取 CSV
    try:
        return pd.read_csv(file_path)

    # 如果 pandas 仍然判定為空資料，就回傳空 DataFrame
    except pd.errors.EmptyDataError:
        return pd.DataFrame(columns=columns)


def append_detection_records(image_name, output_name, detections):
    """
    將單張圖片的偵測結果寫入 detections.csv 與 summary.csv。
    """

    # 確保 CSV 檔案存在
    ensure_csv_files()

    # 取得目前時間
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 建立每個偵測框的資料列
    rows = []

    # 逐一處理 detections 裡的每個偵測結果
    for item in detections:
        rows.append({
            "image_name": image_name,
            "output_name": output_name,
            "class_name": item["class_name"],
            "confidence": round(item["confidence"], 4),
            "x1": item["x1"],
            "y1": item["y1"],
            "x2": item["x2"],
            "y2": item["y2"],
            "created_at": created_at
        })

    # 安全讀取原本的 detections.csv
    old_df = safe_read_csv(Config.DETECTION_CSV, DETECTION_COLUMNS)

    # 如果有偵測結果，就新增到 detections.csv
    if rows:
        new_df = pd.DataFrame(rows)
        final_df = pd.concat([old_df, new_df], ignore_index=True)
    else:
        final_df = old_df

    # 儲存更新後的 detections.csv
    final_df.to_csv(Config.DETECTION_CSV, index=False, encoding="utf-8-sig")

    # 計算這張圖片的總偵測數量
    total_count = len(detections)

    # 如果有偵測結果，計算平均信心分數
    if total_count > 0:
        avg_confidence = sum(item["confidence"] for item in detections) / total_count
    else:
        avg_confidence = 0

    # 統計每個類別的數量
    class_counts = {}

    # 逐一統計類別出現次數
    for item in detections:
        class_name = item["class_name"]
        class_counts[class_name] = class_counts.get(class_name, 0) + 1

    # 建立 summary 資料列
    summary_row = {
        "image_name": image_name,
        "output_name": output_name,
        "total_count": total_count,
        "avg_confidence": round(avg_confidence, 4),
        "class_counts_json": json.dumps(class_counts, ensure_ascii=False),
        "created_at": created_at
    }

    # 安全讀取原本 summary.csv
    summary_df = safe_read_csv(Config.SUMMARY_CSV, SUMMARY_COLUMNS)

    # 新增一列摘要資料
    summary_df = pd.concat(
        [summary_df, pd.DataFrame([summary_row])],
        ignore_index=True
    )

    # 儲存更新後的 summary.csv
    summary_df.to_csv(Config.SUMMARY_CSV, index=False, encoding="utf-8-sig")

    # 回傳這張圖片的統計結果，方便 result.html 顯示
    return summary_row


def load_detection_data():
    # 安全讀取 detections.csv
    return safe_read_csv(Config.DETECTION_CSV, DETECTION_COLUMNS)


def load_summary_data():
    # 安全讀取 summary.csv
    return safe_read_csv(Config.SUMMARY_CSV, SUMMARY_COLUMNS)


def get_overall_stats():
    # 讀取所有圖片摘要資料
    summary_df = load_summary_data()

    # 讀取所有偵測框詳細資料
    detection_df = load_detection_data()

    # 如果還沒有任何摘要資料，回傳預設值
    if summary_df.empty:
        return {
            "image_count": 0,
            "object_count": 0,
            "most_common_class": "無資料",
            "avg_confidence": 0
        }

    # 已分析圖片數
    image_count = len(summary_df)

    # 累積偵測物件數
    object_count = int(summary_df["total_count"].sum())

    # 如果沒有任何偵測框，最常見類別就是無資料
    if detection_df.empty:
        most_common_class = "無資料"
        avg_confidence = 0
    else:
        most_common_class = detection_df["class_name"].value_counts().idxmax()
        avg_confidence = round(float(detection_df["confidence"].mean()), 4)

    # 回傳整體統計結果
    return {
        "image_count": image_count,
        "object_count": object_count,
        "most_common_class": most_common_class,
        "avg_confidence": avg_confidence
    }


def parse_class_counts(class_counts_json):
    # 如果是空值，回傳空字典
    if pd.isna(class_counts_json):
        return {}

    # 嘗試把 JSON 字串轉成字典
    try:
        return json.loads(class_counts_json)
    except json.JSONDecodeError:
        return {}