AI 眼神空间定位服务
====================

基于 MediaPipe + FastAPI 的视线追踪和3D空间定位服务。

运行方式
--------
双击 run.bat 启动服务，然后打开浏览器访问:
http://localhost:8000/docs

API 接口
--------
POST /api/gaze          摄像头模式（需要连接摄像头）
POST /api/gaze/image    图片模式（传 base64 图片，不需要摄像头）
GET  /api/health        健康检查

PyCharm 使用
------------
1. File -> Open -> 选择本文件夹
2. File -> Settings -> Project -> Python Interpreter
3. 添加解释器 -> Existing -> 选择 venv\Scripts\python.exe
4. 右键 main.py -> Run
