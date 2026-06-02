# 設定 matplotlib 使用非互動式後端
# Docker 容器裡通常沒有圖形化視窗，所以要使用 Agg 才能正常輸出圖片檔
import matplotlib
matplotlib.use("Agg")

# 匯入 os，用來建立資料夾與處理檔案路徑
import os

# 匯入 matplotlib.pyplot，用來產生統計圖表
import matplotlib.pyplot as plt

# 匯入 Config，取得圖表輸出資料夾
from config import Config

# 匯入讀取 CSV 的工具函式
from utils.statistics import load_detection_data, load_summary_data


# 設定 Matplotlib 中文字體
# Dockerfile 若已安裝 fonts-noto-cjk，通常可以使用 Noto Sans CJK TC / JP / SC
plt.rcParams["font.sans-serif"] = [
    "Noto Sans CJK TC",
    "Noto Sans CJK JP",
    "Noto Sans CJK SC",
    "DejaVu Sans"
]

# 解決負號顯示成方框的問題
plt.rcParams["axes.unicode_minus"] = False


def style_common_axes(grid_axis="y"):
    # 取得目前圖表的座標軸
    ax = plt.gca()

    # 隱藏上方框線，讓圖表看起來比較乾淨
    ax.spines["top"].set_visible(False)

    # 隱藏右側框線，讓圖表看起來比較乾淨
    ax.spines["right"].set_visible(False)

    # 將左側框線顏色調淡
    ax.spines["left"].set_color("#CBD5E1")

    # 將下方框線顏色調淡
    ax.spines["bottom"].set_color("#CBD5E1")

    # 設定刻度文字顏色
    ax.tick_params(colors="#475569")

    # 加上淡淡的輔助線
    ax.grid(axis=grid_axis, alpha=0.18)

    # 讓輔助線顯示在圖形後方
    ax.set_axisbelow(True)


def save_empty_chart(output_path, title, message):
    # 建立空圖表
    plt.figure(figsize=(10, 5))

    # 設定整張圖背景為白色
    plt.gcf().patch.set_facecolor("white")

    # 設定圖表標題
    plt.title(
        title,
        fontsize=17,
        fontweight="bold",
        color="#0B1F33",
        pad=18
    )

    # 在圖表中央顯示提示文字
    plt.text(
        0.5,
        0.5,
        message,
        ha="center",
        va="center",
        fontsize=14,
        color="#64748B"
    )

    # 關閉座標軸
    plt.axis("off")

    # 自動調整版面
    plt.tight_layout()

    # 儲存圖表
    plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="white")

    # 關閉圖表，避免記憶體累積
    plt.close()


def generate_class_count_chart():
    # 讀取所有偵測框詳細資料
    df = load_detection_data()

    # 確保圖表資料夾存在
    os.makedirs(Config.CHART_FOLDER, exist_ok=True)

    # 設定圖表輸出路徑
    output_path = os.path.join(Config.CHART_FOLDER, "class_count.png")

    # 如果目前沒有任何偵測資料，產生提示圖
    if df.empty:
        save_empty_chart(
            output_path,
            "各類海洋廢棄物數量統計",
            "目前尚無偵測資料，請先上傳圖片進行分析。"
        )
        return output_path

    # 統計每個類別的出現次數，並由小到大排序
    counts = df["class_name"].value_counts().sort_values(ascending=True)

    # 只顯示前 10 個類別，避免圖表太擠
    counts = counts.tail(10)

    # 建立圖表
    plt.figure(figsize=(10, 5.6))

    # 設定整張圖背景為白色
    plt.gcf().patch.set_facecolor("white")

    # 畫橫向長條圖
    bars = plt.barh(
        counts.index,
        counts.values,
        color="#2898AC",
        alpha=0.9
    )

    # 設定圖表標題
    plt.title(
        "各類海洋廢棄物數量統計",
        fontsize=17,
        fontweight="bold",
        color="#0B1F33",
        pad=18
    )

    # 設定 X 軸標籤
    plt.xlabel("偵測數量", fontsize=12, color="#334155")

    # 設定 Y 軸標籤
    plt.ylabel("類別", fontsize=12, color="#334155")

    # 設定 X 軸從 0 開始
    plt.xlim(left=0)

    # 在每個長條右側顯示數字
    for bar in bars:
        # 取得長條寬度
        width = bar.get_width()

        # 顯示數字
        plt.text(
            width + 0.05,
            bar.get_y() + bar.get_height() / 2,
            str(int(width)),
            va="center",
            fontsize=11,
            color="#0B1F33",
            fontweight="bold"
        )

    # 美化座標軸
    style_common_axes(grid_axis="x")

    # 自動調整版面
    plt.tight_layout()

    # 儲存圖表
    plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="white")

    # 關閉圖表
    plt.close()

    # 回傳圖表路徑
    return output_path


def generate_image_count_chart():
    # 讀取每張圖片的摘要資料
    df = load_summary_data()

    # 確保圖表資料夾存在
    os.makedirs(Config.CHART_FOLDER, exist_ok=True)

    # 設定圖表輸出路徑
    output_path = os.path.join(Config.CHART_FOLDER, "image_count.png")

    # 如果目前沒有任何圖片分析紀錄，產生提示圖
    if df.empty:
        save_empty_chart(
            output_path,
            "每張圖片偵測數量",
            "目前尚無圖片分析紀錄，請先上傳圖片進行分析。"
        )
        return output_path

    # 取最近 12 筆紀錄，避免 X 軸太擠
    recent_df = df.tail(12).copy()

    # 建立簡短圖片名稱，避免 UUID 檔名過長
    recent_df["short_name"] = [
        f"第 {i + 1} 張" for i in range(len(recent_df))
    ]

    # 建立圖表
    plt.figure(figsize=(10, 5.6))

    # 設定整張圖背景為白色
    plt.gcf().patch.set_facecolor("white")

    # 畫長條圖
    bars = plt.bar(
        recent_df["short_name"],
        recent_df["total_count"],
        color="#45B1C3",
        alpha=0.9
    )

    # 設定圖表標題
    plt.title(
        "最近圖片偵測數量",
        fontsize=17,
        fontweight="bold",
        color="#0B1F33",
        pad=18
    )

    # 設定 X 軸標籤
    plt.xlabel("最近分析圖片", fontsize=12, color="#334155")

    # 設定 Y 軸標籤
    plt.ylabel("偵測物件數", fontsize=12, color="#334155")

    # 設定 Y 軸從 0 開始
    plt.ylim(bottom=0)

    # 取得最大偵測數量
    max_count = recent_df["total_count"].max()

    # 如果最大值小於 5，讓 Y 軸至少顯示到 5，避免圖表太扁
    if max_count < 5:
        plt.ylim(0, 5)

    # 在每個長條上方顯示數字
    for bar in bars:
        # 取得長條高度
        height = bar.get_height()

        # 顯示數字
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            height + 0.05,
            str(int(height)),
            ha="center",
            va="bottom",
            fontsize=11,
            color="#0B1F33",
            fontweight="bold"
        )

    # 美化座標軸
    style_common_axes(grid_axis="y")

    # 自動調整版面
    plt.tight_layout()

    # 儲存圖表
    plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="white")

    # 關閉圖表
    plt.close()

    # 回傳圖表路徑
    return output_path


def generate_confidence_chart():
    # 讀取偵測框詳細資料
    df = load_detection_data()

    # 確保圖表資料夾存在
    os.makedirs(Config.CHART_FOLDER, exist_ok=True)

    # 設定圖表輸出路徑
    output_path = os.path.join(Config.CHART_FOLDER, "confidence_hist.png")

    # 如果目前沒有任何信心分數資料，產生提示圖
    if df.empty:
        save_empty_chart(
            output_path,
            "信心分數分布",
            "目前尚無信心分數資料，請先上傳圖片進行分析。"
        )
        return output_path

    # 取出信心分數欄位
    confidence_values = df["confidence"]

    # 建立圖表
    plt.figure(figsize=(10, 5.6))

    # 設定整張圖背景為白色
    plt.gcf().patch.set_facecolor("white")

    # 固定信心分數區間為 0 到 1
    bins = [i / 10 for i in range(0, 11)]

    # 畫直方圖
    plt.hist(
        confidence_values,
        bins=bins,
        color="#2898AC",
        edgecolor="white",
        alpha=0.9
    )

    # 設定圖表標題
    plt.title(
        "信心分數分布",
        fontsize=17,
        fontweight="bold",
        color="#0B1F33",
        pad=18
    )

    # 設定 X 軸標籤
    plt.xlabel("信心分數", fontsize=12, color="#334155")

    # 設定 Y 軸標籤
    plt.ylabel("偵測數量", fontsize=12, color="#334155")

    # 固定 X 軸範圍
    plt.xlim(0, 1)

    # 設定 X 軸刻度
    plt.xticks(bins)

    # 設定 Y 軸從 0 開始
    plt.ylim(bottom=0)

    # 美化座標軸
    style_common_axes(grid_axis="y")

    # 在圖表底部加入補充說明
    plt.figtext(
        0.5,
        -0.035,
        "信心分數越接近 1，代表模型對該偵測結果越有把握。",
        ha="center",
        fontsize=11,
        color="#64748B"
    )

    # 自動調整版面
    plt.tight_layout()

    # 儲存圖表
    plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="white")

    # 關閉圖表
    plt.close()

    # 回傳圖表路徑
    return output_path


def generate_all_charts():
    # 產生各類海洋廢棄物數量統計圖
    generate_class_count_chart()

    # 產生最近圖片偵測數量圖
    generate_image_count_chart()

    # 產生信心分數分布圖
    generate_confidence_chart()