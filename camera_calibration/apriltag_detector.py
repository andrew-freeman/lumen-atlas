from pupil_apriltags import Detector
import cv2
import numpy as np

class AprilTagDetector:
    def __init__(self):
        self.detector = Detector(
            families="tag25h9",
            nthreads=2,
            quad_decimate=1,
            quad_sigma=0.8,
            refine_edges=1,
            decode_sharpening=0.25,
            debug=0,
        )

    def detect(self, frame_bgr):
        gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (5, 5), 0.8)
        detections = self.detector.detect(gray)
        #cv2.imshow("apriltag gray", gray)
        #cv2.waitKey(1)
        return detections


def draw_apriltags(frame, detections):
    for d in detections:
        # Corners
        pts = d.corners.astype(int)
        cv2.polylines(frame, [pts], isClosed=True, color=(0, 255, 0), thickness=2)

        # Center
        cx, cy = int(d.center[0]), int(d.center[1])
        cv2.circle(frame, (cx, cy), 5, (0, 0, 255), -1)

        # ID
        cv2.putText(
            frame,
            f"ID {d.tag_id}",
            (cx + 5, cy - 5),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (255, 255, 0),
            1,
        )


def draw_ruler_measurement(frame, detections, known_inches=11.0):
    if len(detections) != 2:
        return None

    d1, d2 = detections
    p1 = d1.center
    p2 = d2.center

    dx = p1[0] - p2[0]
    dy = p1[1] - p2[1]
    dist_px = (dx**2 + dy**2) ** 0.5

    scale = dist_px / known_inches  # px per inch

    x1, y1 = int(p1[0]), int(p1[1])
    x2, y2 = int(p2[0]), int(p2[1])

    cv2.line(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)

    cv2.putText(
        frame,
        f"{dist_px:.1f}px  |  {scale:.2f}px/in",
        ((x1 + x2) // 2, (y1 + y2) // 2 - 10),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (255, 0, 0),
        2,
    )

    return scale
