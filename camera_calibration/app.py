from fastapi import FastAPI
from fastapi.responses import HTMLResponse, StreamingResponse, JSONResponse
import time

from camera import Camera

app = FastAPI(title="lumen-atlas camera console")

camera = Camera(index=0, width=1280, height=720, fps=12, jpeg_quality=80)


@app.get("/health")
def health():
    ok = camera.get_latest_jpeg() is not None
    return JSONResponse({"camera_ok": ok})


@app.get("/")
def index():
    return HTMLResponse(
        """
        <html>
          <head><title>lumen-atlas</title></head>
          <body>
            <h2>Live Camera Feed</h2>
            <p>If this page loads but video doesn't, open <a href="/health">/health</a>.</p>
            <img src="/video" style="max-width: 100%; height: auto;" />
          </body>
        </html>
        """
    )


def mjpeg_generator():
    # This generator yields the *latest* JPEG repeatedly.
    # It does not accumulate frames -> bounded memory.
    boundary = b"--frame"
    try:
        while True:
            jpeg = camera.get_latest_jpeg()
            if jpeg is None:
                time.sleep(0.05)
                continue

            yield boundary + b"\r\n"
            yield b"Content-Type: image/jpeg\r\n"
            yield f"Content-Length: {len(jpeg)}\r\n\r\n".encode("ascii")
            yield jpeg + b"\r\n"

            # Important: keep loop gentle even if camera thread is faster
            time.sleep(0.02)
    except GeneratorExit:
        # Client disconnected
        return


@app.get("/video")
def video():
    return StreamingResponse(
        mjpeg_generator(),
        media_type="multipart/x-mixed-replace; boundary=frame",
        headers={
            "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
            "Pragma": "no-cache",
        },
    )
