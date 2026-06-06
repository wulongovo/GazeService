"""
AI 眼神空间定位服务 v2.0
基于 MediaPipe Task API + FastAPI

两种模式：
  POST /api/gaze          → 摄像头模式（需要连接摄像头）
  POST /api/gaze/image    → 图片模式（传 base64，不需要摄像头）
"""

import cv2
import numpy as np
import mediapipe as mp
import base64
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn

# ======================
# 1. MediaPipe 初始化（延迟加载）
# ======================
_face_landmarker = None
_MODEL_PATH = os.path.join(os.getcwd(), "face_landmarker.task")

def get_landmarker():
    global _face_landmarker
    if _face_landmarker is None:
        BaseOptions = mp.tasks.BaseOptions
        FaceLandmarker = mp.tasks.vision.FaceLandmarker
        FaceLandmarkerOptions = mp.tasks.vision.FaceLandmarkerOptions
        VisionRunningMode = mp.tasks.vision.RunningMode

        options = FaceLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=_MODEL_PATH),
            running_mode=VisionRunningMode.IMAGE,
            num_faces=1,
            min_face_detection_confidence=0.5,
            min_face_presence_confidence=0.5,
            min_tracking_confidence=0.5,
            output_facial_transformation_matrixes=True,
        )
        _face_landmarker = FaceLandmarker.create_from_options(options)
    return _face_landmarker

# ======================
# 2. FastAPI 初始化
# ======================
app = FastAPI(
    title="AI 眼神空间定位服务",
    description="基于 MediaPipe + FastAPI 的视线追踪、3D空间定位、屏幕注视点服务",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ImageRequest(BaseModel):
    image_base64: str

# ======================
# 3. 核心计算函数
# ======================

def get_eye_gaze(landmarks, w, h):
    lp = landmarks[468]   # 左眼虹膜中心
    rp = landmarks[473]   # 右眼虹膜中心
    lx, ly = lp.x * w, lp.y * h
    rx, ry = rp.x * w, rp.y * h
    gx = (lx + rx) / 2
    gy = (ly + ry) / 2
    return {
        "gaze_norm":  (float(np.clip(gx / w, 0, 1)), float(np.clip(gy / h, 0, 1))),
        "left_eye":   (float(lx), float(ly)),
        "right_eye":  (float(rx), float(ry)),
    }

def estimate_head_pose(landmarks, w, h):
    indices = [1, 33, 61, 199, 263, 291]
    pts_2d, pts_3d = [], []
    for i in indices:
        lm = landmarks[i]
        x, y = lm.x * w, lm.y * h
        pts_2d.append([x, y])
        pts_3d.append([x, y, lm.z])
    pts_2d = np.array(pts_2d, dtype=np.float64)
    pts_3d = np.array(pts_3d, dtype=np.float64)
    cam = np.array([[w, 0, w / 2], [0, w, h / 2], [0, 0, 1]], dtype=np.float64)
    dist = np.zeros((4, 1), dtype=np.float64)
    ok, rvec, tvec = cv2.solvePnP(pts_3d, pts_2d, cam, dist)
    if not ok:
        return 0.0, 0.0, 0.0
    rmat, _ = cv2.Rodrigues(rvec)
    angles, _, _, _, _, _ = cv2.RQDecomp3x3(rmat)
    return float(angles[0]), float(angles[1]), float(angles[2])

# ======================
# 4. 帧处理核心
# ======================

def process_frame(frame):
    landmarker = get_landmarker()
    h, w = frame.shape[:2]
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
    result = landmarker.detect(mp_image)

    if not result.face_landmarks or len(result.face_landmarks) == 0:
        return {"status": "no_face", "message": "未检测到人脸"}

    landmarks = result.face_landmarks[0]
    gaze = get_eye_gaze(landmarks, w, h)
    pitch, yaw, roll = estimate_head_pose(landmarks, w, h)
    gaze_z = float(landmarks[4].z)

    facial_transform = None
    if result.facial_transformation_matrixes and len(result.facial_transformation_matrixes) > 0:
        mat = result.facial_transformation_matrixes[0]
        facial_transform = [[round(float(mat[i][j]), 4) for j in range(4)] for i in range(4)]

    gx, gy = gaze["gaze_norm"]
    return {
        "status": "success",
        "gaze": {"x": round(gx, 4), "y": round(gy, 4), "z": round(gaze_z, 4)},
        "screen_point": {"x": round(gx, 4), "y": round(gy, 4)},
        "head_pose": {"pitch": round(pitch, 4), "yaw": round(yaw, 4), "roll": round(roll, 4)},
        "left_eye": {"x": round(gaze["left_eye"][0], 2), "y": round(gaze["left_eye"][1], 2)},
        "right_eye": {"x": round(gaze["right_eye"][0], 2), "y": round(gaze["right_eye"][1], 2)},
        "frame_size": {"width": w, "height": h},
        "facial_transformation_matrix": facial_transform
    }

# ======================
# 5. API 接口
# ======================

@app.get("/")
def index():
    return {"message": "AI 眼神空间定位服务运行中", "version": "2.0.0"}

@app.get("/api/health")
def health():
    return {"status": "running"}

@app.post("/api/gaze")
def gaze_from_camera():
    """模式1：摄像头模式（需要连接摄像头）"""
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        return JSONResponse(status_code=500, content={
            "error": "摄像头未连接或无法打开",
            "hint": "请连接摄像头，或使用 POST /api/gaze/image 传图片"
        })
    ret, frame = cap.read()
    cap.release()
    if not ret or frame is None:
        return JSONResponse(status_code=500, content={"error": "摄像头读取失败"})
    return process_frame(frame)

@app.post("/api/gaze/image")
def gaze_from_image(req: ImageRequest):
    """模式2：图片模式（不需要摄像头）
    传入 base64 图片，支持纯 base64 或 data:image/xxx;base64, 前缀
    """
    try:
        b64 = req.image_base64
        if "," in b64:
            b64 = b64.split(",", 1)[1]
        img_bytes = base64.b64decode(b64)
        arr = np.frombuffer(img_bytes, dtype=np.uint8)
        frame = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        if frame is None:
            return JSONResponse(status_code=400, content={"error": "图片解码失败"})
        return process_frame(frame)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

# ======================
# 6. 挂载前端页面
# ======================
_static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
if os.path.isdir(_static_dir):
    from fastapi.staticfiles import StaticFiles
    app.mount("/", StaticFiles(directory=_static_dir, html=True), name="static")

# ======================
# 7. 启动
# ======================
if __name__ == "__main__":
    print("正在加载 MediaPipe 模型...")
    get_landmarker()
    print("模型加载完成，启动服务...")
    print("访问 http://localhost:8000/docs 查看 API 文档")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
