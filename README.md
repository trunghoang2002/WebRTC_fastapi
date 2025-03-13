# WebRTC_fastapi

## Pre-requisites

Before you begin, ensure you have met the following requirements:
- **Python 3.7 or higher**: The project is built using Python, so you need to have Python installed on your system.
- **OpenCV**: Required for video capture and processing.
- **aiortc**: A library for WebRTC and media streaming in Python.
- **FastAPI**: A modern, fast (high-performance) web framework for building APIs with Python.
- **Uvicorn**: A lightning-fast ASGI server for serving the FastAPI application.

## Installation

To install all dependencies for this project, follow these steps:

1. **Clone the repository**:
   ```bash
   git clone https://github.com/trunghoang2002/WebRTC_fastapi.git
   cd WebRTC_fastapi
   ```

2. **Create a virtual environment** (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. **Install the required dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

   Alternatively, you can install the dependencies manually:
   ```bash
   pip install fastapi uvicorn[standard] opencv-python aiortc
   ```

4. **Ensure you have a video file**:
   - Place a video file named `video.mp4` in the root directory of the project (if you want to stream from a local file).

## Running the Project

To run the server, use the following command:

1. **Start the FastAPI server**:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

2. **Access the application**:
   - Open your browser and navigate to `http://localhost:8000`.
   - You should see a web page with buttons to start streaming from the camera or a local video file.

3. **Using the application**:
   - **Start Camera**: Click the "Start Camera" button to stream video from your webcam.
   - **Start Local File**: Click the "Start Local File" button to stream video from the `video.mp4` file.
   - **Stop Stream**: Click the "Stop Stream" button to stop the current stream.
   - **Start Recording**: Click the "Start Recording" button to start recording the video stream.
   - **Stop Recording**: Click the "Stop Recording" button to stop recording and download the video.

## Project Structure

- `main.py`: The main FastAPI server file that handles WebSocket connections and WebRTC signaling.
- `templates/index.html`: The HTML template for the client interface.
- `static/script.js`: The JavaScript file for handling client-side WebRTC and WebSocket communication.
- `static/styles.css`: The CSS file for styling the client interface.
- `video.mp4`: A sample video file for local video streaming (you need to provide this file).

## Troubleshooting

- **Camera not working**: Ensure your webcam is properly connected and accessible by the application.
- **Video file not found**: Ensure the `video.mp4` file exists in the root directory of the project.
- **WebSocket connection issues**: Ensure the server is running and accessible at `ws://localhost:8000/ws`.

## Contributing

If you'd like to contribute to this project, please follow these steps:
1. Fork the repository.
2. Create a new branch (`git checkout -b feature/YourFeatureName`).
3. Commit your changes (`git commit -m 'Add some feature'`).
4. Push to the branch (`git push origin feature/YourFeatureName`).
5. Open a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---