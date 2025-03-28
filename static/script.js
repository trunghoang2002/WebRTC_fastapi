const video = document.getElementById('video');
const configuration = {
    iceServers: [
      {
        urls: [
            'stun:stun.l.google.com:19302',
            'stun:stun1.l.google.com:19302',
            'stun:stun2.l.google.com:19302',
        ],
      },
    ],
    // iceCandidatePoolSize: 10,
};

let pc; // RTCPeerConnection
let ws; // WebSocket

// Hàm khởi tạo RTCPeerConnection và WebSocket
function initializeConnection() {
    // pc = new RTCPeerConnection();
    pc = new RTCPeerConnection(configuration);
    ws = new WebSocket('ws://localhost:8000/ws');
    // ws = new WebSocket('wss://vast-alien-obviously.ngrok-free.app/ws'); // use: ngrok http --url=vast-alien-obviously.ngrok-free.app 8000

    // Xử lý khi nhận được track video từ server
    pc.ontrack = function (event) {
        if (event.track.kind === 'video') {
            console.log("Video track received");
            video.srcObject = event.streams[0];
            video.play();
        }
    };

    // Xử lý khi có ICE candidate được tạo
    pc.onicecandidate = (event) => {
        if (event.candidate) {
            console.log("Sending ICE candidate to server");
            ws.send(JSON.stringify({
                type: 'candidate',
                candidate: event.candidate
            }));
        }
    };

    // Xử lý khi ICE connection state thay đổi
    pc.oniceconnectionstatechange = function () {
        console.log("ICE connection state:", pc.iceConnectionState);
        if (pc.iceConnectionState === "failed") {
            console.error("ICE connection failed");
        }
    };
    
    // Xử lý khi ICE gathering state thay đổi
    pc.onicegatheringstatechange = function () {
        console.log("IICE gathering state changed to:", pc.iceGatheringState);
        if (pc.iceGatheringState === "complete") {
            console.log("All ICE candidates have been gathered.");
        }
    };

    pc.onsignalingstatechange = function () {
        console.log("Signaling state change:", pc.signalingState);
        if (pc.signalingState === "stable") {
            console.log("ICE gathering complete");
        }
    };
    
    // Xử lý khi connection state thay đổi
    pc.onconnectionstatechange = function () {
        console.log("Connection state change:", pc.connectionState);
        if (pc.connectionState === "connected") {
            console.log("Peers successfully connected");
        }
    };

    // Xử lý tin nhắn từ WebSocket
    ws.onmessage = async function (event) {
        const message = JSON.parse(event.data);
        if (message.type === 'offer') {
            if (pc.signalingState === 'closed') {
                console.error("RTCPeerConnection is closed, cannot set remote description");
                return;
            }
            // Đặt Offer từ server
            console.log("Received offer from server");
            await pc.setRemoteDescription(new RTCSessionDescription(message));
            // Tạo Answer
            const answer = await pc.createAnswer();
            await pc.setLocalDescription(answer);
            // Gửi Answer về server
            console.log("Sending answer to server");
            ws.send(JSON.stringify({
                type: "answer",
                sdp: answer.sdp
            }));
        } else if (message.type === 'candidate') {
            if (pc.signalingState === 'closed') {
                console.error("RTCPeerConnection is closed, cannot add ICE candidate");
                return;
            }
            console.log("Received ICE candidate from server");
            await pc.addIceCandidate(new RTCIceCandidate(message.candidate));
        }
    };

    ws.onerror = function (error) {
        console.error("WebSocket error:", error);
    };

    ws.onclose = function () {
        console.log("WebSocket connection closed");
    };
}

// Hàm bắt đầu stream video
async function startStream(source) {
    // Đảm bảo đóng kết nối cũ trước khi bắt đầu kết nối mới
    stopStream();

    // Khởi tạo kết nối mới
    initializeConnection();

    // Đợi WebSocket mở
    ws.onopen = function () {
        console.log("WebSocket connection established");
        ws.send(JSON.stringify({ type: 'start', source: source }));
    };
}

// Hàm dừng stream video
function stopStream() {
    if (ws) {
        ws.close(); // Đóng WebSocket
    }
    if (pc) {
        pc.close(); // Đóng RTCPeerConnection
    }
    if (video.srcObject) {
        video.srcObject.getTracks().forEach(track => track.stop()); // Dừng các track video
        video.srcObject = null; // Xóa video stream
    }
    console.log("Stream stopped");
}

// Biến để quản lý MediaRecorder
let mediaRecorder;
let recordedChunks = [];

// Hàm bắt đầu ghi lại video
function startRecording(stream) {
    if (!stream) {
        console.error("No stream available to record");
        return;
    }
    recordedChunks = [];
    mediaRecorder = new MediaRecorder(stream);
    mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
            recordedChunks.push(event.data);
        }
    };
    mediaRecorder.onstop = () => {
        const blob = new Blob(recordedChunks, { type: 'video/webm' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'recorded-video.webm';
        a.click();
        URL.revokeObjectURL(url);
    };
    mediaRecorder.start();
    console.log("Recording started");
}

// Hàm dừng ghi lại video
function stopRecording() {
    if (mediaRecorder && mediaRecorder.state === 'recording') {
        mediaRecorder.stop();
        console.log("Recording stopped");
    }
}

// Gán sự kiện cho các nút
document.getElementById('start-camera').onclick = () => startStream('camera');
document.getElementById('start-file').onclick = () => startStream('file');
document.getElementById('stop-stream').onclick = () => stopStream();
document.getElementById('start-recording').onclick = () => startRecording(video.srcObject);
document.getElementById('stop-recording').onclick = () => stopRecording();