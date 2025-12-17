import cv2
import threading
import time
from apriltag_detector import AprilTagDetector, draw_apriltags, draw_ruler_measurement

class Camera:
    def __init__(self, index=0, width=1920, height=1080, fps=15, jpeg_quality=90):
        self.cap = cv2.VideoCapture(index, cv2.CAP_V4L2)
        if not self.cap.isOpened():
            raise RuntimeError(f"Cannot open camera index={index}")

        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        self.cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1)   # may be 0 or 1 depending on driver
        self.cap.set(cv2.CAP_PROP_EXPOSURE, -5)       # try -4 .. -7

        self.fps = max(1, int(fps))
        self.jpeg_quality = int(jpeg_quality)

        self._latest_jpeg = None
        self._lock = threading.Lock()
        self._running = True

        self.tag_detector = AprilTagDetector()
        
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()
        
        

    def _loop(self):
        delay = 1.0 / self.fps
        encode_params = [int(cv2.IMWRITE_JPEG_QUALITY), self.jpeg_quality]

        while self._running:
            ret, frame = self.cap.read()
            if not ret:
                time.sleep(0.05)
                continue

            detections = self.tag_detector.detect(frame)
            
            if detections:
                print(f"Detected {len(detections)} tags")
            else:
                print("no detected tags")
    
            draw_apriltags(frame, detections)
            draw_ruler_measurement(frame, detections, known_inches=11.0)

            ok, jpeg = cv2.imencode(".jpg", frame, encode_params)
            if ok:
                with self._lock:
                    self._latest_jpeg = jpeg.tobytes()

            time.sleep(delay)

    def get_latest_jpeg(self):
        with self._lock:
            return self._latest_jpeg

    def release(self):
        self._running = False
        self._thread.join(timeout=1.0)
        self.cap.release()
