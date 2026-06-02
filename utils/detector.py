# 匯入 os，用來檢查模型檔案是否存在與取得檔案大小
import os

# 匯入 cv2，用來讀取圖片、畫框、儲存圖片
import cv2

# 從 ultralytics 匯入 YOLO 模型
from ultralytics import YOLO

# 從 config 匯入專案設定
from config import Config


# COCO 預訓練模型中的部分類別，轉成比較接近海洋廢棄物的名稱
# 注意：這只是第一版流程測試用，不是真正的海洋廢棄物模型
COCO_TO_DEBRIS_NAME = {
    "bottle": "plastic_bottle",
    "cup": "plastic_cup",
    "bowl": "container",
    "backpack": "bag",
    "handbag": "bag",
    "suitcase": "large_container",
}


# fallback 模型只保留比較可能和垃圾有關的 COCO 類別
FALLBACK_ALLOWED_CLASSES = set(COCO_TO_DEBRIS_NAME.keys())


# 全域變數：避免每次上傳圖片都重新載入模型
_model = None

# 全域變數：記錄目前是否使用自訂模型
_is_custom_model = False


def is_valid_model_file(model_path):
    # 檢查模型檔是否存在
    if not os.path.exists(model_path):
        return False

    # 檢查模型檔大小是否大於 1MB
    # 如果是 0B 或很小，通常代表檔案是空的或壞掉的
    if os.path.getsize(model_path) < 1024 * 1024:
        return False

    # 通過檢查，代表模型檔看起來是有效的
    return True


def get_model():
    # 使用 global，讓函式可以修改外層變數
    global _model, _is_custom_model

    # 如果模型已經載入過，就直接回傳
    if _model is not None:
        return _model, _is_custom_model

    # 如果 models/best.pt 存在且不是空檔，才使用自訂模型
    if is_valid_model_file(Config.CUSTOM_MODEL_PATH):
        try:
            # 載入自訂 YOLOv8 模型
            _model = YOLO(Config.CUSTOM_MODEL_PATH)

            # 標記目前使用自訂模型
            _is_custom_model = True

            # 回傳模型
            return _model, _is_custom_model

        except Exception:
            # 如果 best.pt 雖然存在但讀取失敗，就改用 fallback 模型
            _model = None
            _is_custom_model = False

    # 如果沒有可用的 best.pt，就使用 YOLOv8 nano 預訓練模型
    _model = YOLO(Config.FALLBACK_MODEL_NAME)

    # 標記目前不是自訂模型
    _is_custom_model = False

    # 回傳模型
    return _model, _is_custom_model


def normalize_class_name(raw_name, is_custom_model):
    # 如果是自訂模型，就直接使用模型原本的類別名稱
    if is_custom_model:
        return raw_name.replace(" ", "_").lower()

    # 如果是 fallback 模型，就把 COCO 類別名稱轉成海廢相關名稱
    return COCO_TO_DEBRIS_NAME.get(raw_name, raw_name.replace(" ", "_").lower())


def run_detection(input_path, output_path):
    # 載入 YOLO 模型
    model, is_custom_model = get_model()

    # 使用 YOLOv8 對圖片進行預測
    results = model.predict(
        source=input_path,
        conf=Config.CONFIDENCE_THRESHOLD,
        imgsz=640,
        save=False,
        verbose=False
    )

    # 使用 OpenCV 讀取原始圖片
    image = cv2.imread(input_path)

    # 如果圖片讀取失敗，回傳錯誤
    if image is None:
        raise ValueError("圖片讀取失敗，請確認圖片格式是否正確。")

    # 建立空清單，用來儲存偵測結果
    detections = []

    # 取得第一張圖片的偵測結果
    result = results[0]

    # 取得模型類別名稱
    names = result.names

    # 如果沒有偵測到任何物件，就直接儲存原圖
    if result.boxes is None or len(result.boxes) == 0:
        cv2.imwrite(output_path, image)
        return detections

    # 逐一處理每個偵測框
    for box in result.boxes:
        # 取得類別編號
        class_id = int(box.cls[0])

        # 取得原始類別名稱
        raw_class_name = names[class_id]

        # 如果使用 fallback 模型，只保留比較可能是垃圾的類別
        if not is_custom_model and raw_class_name not in FALLBACK_ALLOWED_CLASSES:
            continue

        # 轉換類別名稱
        class_name = normalize_class_name(raw_class_name, is_custom_model)

        # 取得信心分數
        confidence = float(box.conf[0])

        # 取得框線座標
        x1, y1, x2, y2 = box.xyxy[0].tolist()

        # 座標轉成整數
        x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

        # 在圖片上畫框
        cv2.rectangle(
            image,
            (x1, y1),
            (x2, y2),
            (0, 166, 180),
            2
        )

        # 建立標籤文字
        label = f"{class_name} {confidence:.2f}"

        # 在圖片上寫類別與信心分數
        cv2.putText(
            image,
            label,
            (x1, max(y1 - 10, 20)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 166, 180),
            2
        )

        # 把偵測結果加入清單
        detections.append({
            "class_name": class_name,
            "confidence": confidence,
            "x1": x1,
            "y1": y1,
            "x2": x2,
            "y2": y2
        })

    # 儲存畫框後圖片
    cv2.imwrite(output_path, image)

    # 回傳偵測結果
    return detections