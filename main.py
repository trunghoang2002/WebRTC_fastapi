from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles  # Để phục vụ file tĩnh (CSS, JS)
import cv2
import asyncio
from aiortc import RTCPeerConnection, RTCSessionDescription, VideoStreamTrack
from aiortc.contrib.signaling import TcpSocketSignaling
from aiortc import RTCConfiguration, RTCIceServer, RTCIceCandidate
from av import VideoFrame
import fractions
from datetime import datetime
import numpy as np
import json
from collections import defaultdict  # Quản lý nhiều kết nối

# -------------------------------------------------------------------
# Lớp CustomVideoStreamTrack: tạo video track từ camera hoặc file video.
# -------------------------------------------------------------------
class CustomVideoStreamTrack(VideoStreamTrack):
    def __init__(self, source):
        super().__init__()
        self.source = source
        if source == 'camera':
            self.cap = cv2.VideoCapture(0)  # Mở camera mặc định
        else:
            self.cap = cv2.VideoCapture('video.mp4')  # Mở file video local
            if not self.cap.isOpened():
                print("Error: Could not open video file")
        self.frame_count = 0

    async def recv(self):
        self.frame_count += 1
        ret, frame = self.cap.read()
        if not ret:
            print("Failed to read frame from source")
            if self.source != 'camera':  # Nếu là file video, đặt lại vị trí về đầu
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                ret, frame = self.cap.read()
                if not ret:
                    print("Error: Could not reset video to the beginning")
                    return None
        # Chuyển đổi frame sang định dạng RGB
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # Thêm timestamp vào frame
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        cv2.putText(frame, timestamp, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
        # Tạo VideoFrame từ numpy array
        video_frame = VideoFrame.from_ndarray(frame, format="rgb24")
        video_frame.pts = self.frame_count
        video_frame.time_base = fractions.Fraction(1, 30)
        return video_frame

# -------------------------------------------------------------------
# Khởi tạo ứng dụng FastAPI
# -------------------------------------------------------------------
app = FastAPI()

# -------------------------------------------------------------------
# Phục vụ các file tĩnh (CSS, JS) từ thư mục "static"
# -------------------------------------------------------------------
app.mount("/static", StaticFiles(directory="static"), name="static")

# -------------------------------------------------------------------
# Endpoint HTTP: phục vụ trang HTML client
# -------------------------------------------------------------------
@app.get("/")
async def get():
    with open("templates/index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())

# Cấu hình STUN/TURN server
RTC_CONFIGURATION = RTCConfiguration([
    RTCIceServer(urls="stun:stun.l.google.com:19302"),
    RTCIceServer(urls="stun:stun1.l.google.com:19302"),
    RTCIceServer(urls="stun:stun2.l.google.com:19302"),
    # Thêm TURN server nếu cần (ví dụ: "turn:your-turn-server.com")
])

# -------------------------------------------------------------------
# Quản lý nhiều kết nối WebSocket và RTCPeerConnection
# -------------------------------------------------------------------
connections = defaultdict(dict)

# -------------------------------------------------------------------
# Endpoint WebSocket: dùng làm signaling cho kết nối WebRTC
# Mỗi khi có client kết nối, tạo một RTCPeerConnection mới và thêm video track.
# -------------------------------------------------------------------
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("WebSocket connection established")
    pc = RTCPeerConnection()
    # pc = RTCPeerConnection(configuration=RTC_CONFIGURATION)
    video_track = None
    connections[websocket] = {"pc": pc, "video_track": video_track}

    # @pc.on("iceconnectionstatechange")
    # async def on_iceconnectionstatechange():
    #     print(f"ICE connection state: {pc.iceConnectionState}")
    #     if pc.iceConnectionState == "failed":
    #         await pc.close()
    #         del connections[websocket]

    # @pc.on("track")
    # def on_track(track):
    #     print(f"Track received: {track.kind}")
    #     if track.kind == "video":
    #         print("Video track added")

    try:
        while True:
            data = await websocket.receive_text()
            print(f"Received data: {data}")
            message = json.loads(data)
            if message['type'] == 'start':
                print(f"Starting video stream from: {message['source']}")
                video_track = CustomVideoStreamTrack(message['source'])
                pc.addTrack(video_track)
                offer = await pc.createOffer()
                await pc.setLocalDescription(offer)
                print(f"Sending offer: {pc.localDescription.sdp}")
                await websocket.send_text(json.dumps({
                    "type": "offer",
                    "sdp": pc.localDescription.sdp
                }))
            elif message['type'] == 'answer':
                print("Received answer from client")
                await pc.setRemoteDescription(RTCSessionDescription(
                    sdp=message['sdp'],
                    type=message['type']
                ))
            # elif message['type'] == 'candidate':
            #     print("Received ICE candidate from client")
            #     await pc.addIceCandidate(RTCIceCandidate(message['candidate']))
    except WebSocketDisconnect:
        print("Client disconnected")
        await pc.close()
        del connections[websocket]
    except Exception as e:
        print(f"Error: {e}")
        await pc.close()
        del connections[websocket]

# -------------------------------------------------------------------
# Chạy ứng dụng bằng lệnh: uvicorn main:app --host 0.0.0.0 --port 8000
# -------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)