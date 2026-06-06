# 👁️ GazeService - AI 眼神空间定位服务

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/FastAPI-0.100+-009688?style=flat-square&logo=fastapi&logoColor=white" />
  <img src="https://img.shields.io/badge/MediaPipe-Latest-FF6F00?style=flat-square&logo=google&logoColor=white" />
  <img src="https://img.shields.io/badge/OpenCV-4.x-5C3EE8?style=flat-square&logo=opencv&logoColor=white" />
  <img src="https://img.shields.io/badge/License-MIT-green?style=flat-square" />
</p>

基于 **MediaPipe FaceLandmarker + FastAPI** 的实时眼动追踪与3D空间定位服务。通过摄像头或图片输入，实时输出视线方向、头部姿态、3D空间坐标等数据。

---

## ✨ 功能特性

- 🎯 **实时眼动追踪** — 虹膜中心定位 + 视线方向计算
- 🔄 **头部姿态估计** — Pitch / Yaw / Roll 三轴角度
- 📍 **3D空间定位** — 面部变换矩阵 + 空间坐标
- 🖥️ **屏幕注视点** — 归一化注视坐标映射
- 📡 **REST API** — FastAPI 提供标准化接口
- 🌐 **双模式输入** — 摄像头实时 / 图片Base64

## 📦 技术栈

| 组件 | 说明 |
|------|------|
| MediaPipe FaceLandmarker | 人脸关键点检测（478个关键点 + 虹膜） |
| FastAPI | 高性能异步 Web 框架 |
| OpenCV | 图像处理 + PnP 头部姿态解算 |
| NumPy | 矩阵运算 |
| Uvicorn | ASGI 服务器 |

## 🚀 快速开始

### 环境要求

- Python 3.10+
- 摄像头（摄像头模式需要）

### 安装运行

```bash
# 克隆项目
git clone https://github.com/wulongovo/GazeService.git
cd GazeService

# 创建虚拟环境
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# 安装依赖
pip install mediapipe fastapi uvicorn opencv-python-headless numpy

# 启动服务
python main.py
```

启动后访问 http://localhost:8000/docs 查看 API 文档。

## 📡 API 接口

### `GET /` — 服务状态

```json
{"message": "AI 眼神空间定位服务运行中", "version": "2.0.0"}
```

### `POST /api/gaze` — 摄像头模式

连接摄像头，自动拍照并分析。

**响应示例：**

```json
{
  "status": "success",
  "gaze": {"x": 0.52, "y": 0.41, "z": -0.03},
  "screen_point": {"x": 0.52, "y": 0.41},
  "head_pose": {"pitch": -2.35, "yaw": 5.12, "roll": 0.87},
  "left_eye": {"x": 320.5, "y": 240.3},
  "right_eye": {"x": 412.8, "y": 238.7},
  "frame_size": {"width": 640, "height": 480},
  "facial_transformation_matrix": [[...]]
}
```

### `POST /api/gaze/image` — 图片模式

传入 Base64 图片，支持纯 Base64 或 `data:image/xxx;base64,` 前缀。

```json
{"image_base64": "data:image/jpeg;base64,/9j/4AAQ..."}
```

## 🏗️ 项目架构

```
GazeService/
├── main.py                 # FastAPI 主程序
├── face_landmarker.task    # MediaPipe 人脸关键点模型
├── static/
│   └── index.html          # 前端演示页面
├── run.bat                 # Windows 启动脚本
└── start_public.bat        # 公网访问启动脚本
```

## 🔬 核心算法

### 眼动追踪

利用 MediaPipe 的 478 个人脸关键点中的 **虹膜关键点**（#468 左眼, #473 右眼），计算双眼虹膜中心的归一化坐标，得到视线方向。

### 头部姿态估计

选取 6 个关键面部特征点（鼻尖、眼角、嘴角等），结合 **OpenCV 的 PnP 算法** 解算旋转向量，再通过 RQ 分解得到 Pitch/Yaw/Roll 三轴角度。

## 💡 应用场景

| 场景 | 说明 |
|------|------|
| 🚗 驾驶员监测 | 疲劳检测、注意力分散预警 |
| 🎮 人机交互 | 眼神控制界面、注视触发操作 |
| 📊 用户研究 | 注意力热力图、UI可用性分析 |
| ♿ 无障碍辅助 | 眼控打字、视线鼠标 |
| 🎓 在线教育 | 学生注意力监测 |

## 📄 License

MIT License

---

<p align="center">
  ⭐ 如果这个项目对你有帮助，请点个 Star！
</p>
