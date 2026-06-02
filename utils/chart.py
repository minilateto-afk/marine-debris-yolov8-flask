# 設定 matplotlib 使用非互動式後端，避免 Docker 裡沒有 GUI 出錯
import matplotlib
matplotlib.use("Agg")

# 匯入 os，用來建立資料夾與路徑
import os

# 匯入 pandas，用來處理資料
import pandas as pd

# 匯入 matplotlib.pyplot，用來畫圖
import matplotlib.pyplot as plt

# 匯入 Config 設定
from config import Config

# 匯入讀取 CSV 的工具函式
from utils.statistics import load_detection_data, load_summary_data


def generate_class_count_chart():
    # 讀取偵測框詳細資料
    df = load_detection_data()

    # 設定圖表輸出路徑
    output_path = os.path.join(Config.CHART_FOLDER, "class_count.png")

    # 建立圖表資料夾
    os.makedirs(Config.CHART_FOLDER, exist_ok=True)

    # 如果沒有資料，就產生空圖表
    if df.empty:
        plt.figure(figsize=(8, 4))
        plt.title("Class Count")
        plt.text(0.5, 0.5, "No detection data", ha="center", va="center")
        plt.axis("off")
        plt.tight_layout()
        plt.savefig(output_path)
        plt.close()
        return output_path

    # 統計每個類別的數量
    counts = df["class_name"].value_counts()

    # 建立圖表
    plt.figure(figsize=(9, 5))

    # 畫長條圖
    counts.plot(kind="bar")

    # 設定標題
    plt.title("Marine Debris Class Count")

    # 設定 X 軸標籤
    plt.xlabel("Class")

    # 設定 Y 軸標籤
    plt.ylabel("Count")

    # 旋轉 X 軸文字，避免擠在一起
    plt.xticks(rotation=30, ha="right")

    # 自動調整版面
    plt.tight_layout()

    # 儲存圖片
    plt.savefig(output_path)

    # 關閉圖表，避免記憶體累積
    plt.close()

    # 回傳圖表路徑
    return output_path


def generate_image_count_chart():
    # 讀取每張圖片摘要資料
    df = load_summary_data()

    # 設定圖表輸出路徑
    output_path = os.path.join(Config.CHART_FOLDER, "image_count.png")

    # 建立圖表資料夾
    os.makedirs(Config.CHART_FOLDER, exist_ok=True)

    # 如果沒有資料，就產生空圖表
    if df.empty:
        plt.figure(figsize=(8, 4))
        plt.title("Image Count")
        plt.text(0.5, 0.5, "No summary data", ha="center", va="center")
        plt.axis("off")
        plt.tight_layout()
        plt.savefig(output_path)
        plt.close()
        return output_path

    # 只取最近 15 筆，避免圖片太多導致圖表擠在一起
    recent_df = df.tail(15)

    # 建立圖表
    plt.figure(figsize=(10, 5))

    # 畫每張圖片的偵測總數長條圖
    plt.bar(recent_df["image_name"], recent_df["total_count"])

    # 設定標題
    plt.title("Detected Objects per Image")

    # 設定 X 軸標籤
    plt.xlabel("Image")

    # 設定 Y 軸標籤
    plt.ylabel("Total Count")

    # 旋轉 X 軸文字
    plt.xticks(rotation=30, ha="right")

    # 自動調整版面
    plt.tight_layout()

    # 儲存圖表
    plt.savefig(output_path)

    # 關閉圖表
    plt.close()

    # 回傳圖表路徑
    return output_path


def generate_confidence_chart():
    # 讀取偵測框詳細資料
    df = load_detection_data()

    # 設定圖表輸出路徑
    output_path = os.path.join(Config.CHART_FOLDER, "confidence_hist.png")

    # 建立圖表資料夾
    os.makedirs(Config.CHART_FOLDER, exist_ok=True)

    # 如果沒有資料，就產生空圖表
    if df.empty:
        plt.figure(figsize=(8, 4))
        plt.title("Confidence Distribution")
        plt.text(0.5, 0.5, "No confidence data", ha="center", va="center")
        plt.axis("off")
        plt.tight_layout()
        plt.savefig(output_path)
        plt.close()
        return output_path

    # 建立圖表
    plt.figure(figsize=(8, 5))

    # 畫信心分數分布圖
    plt.hist(df["confidence"], bins=10)

    # 設定標題
    plt.title("Confidence Distribution")

    # 設定 X 軸
    plt.xlabel("Confidence")

    # 設定 Y 軸
    plt.ylabel("Frequency")

    # 自動調整版面
    plt.tight_layout()

    # 儲存圖表
    plt.savefig(output_path)

    # 關閉圖表
    plt.close()

    # 回傳圖表路徑
    return output_path


def generate_all_charts():
    # 產生各類海洋廢棄物數量圖
    generate_class_count_chart()

    # 產生每張圖片偵測數量圖
    generate_image_count_chart()

    # 產生信心分數分布圖
    generate_confidence_chart()