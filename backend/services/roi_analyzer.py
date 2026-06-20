## used to calculate ROI complexity metrics
## How important or visually complex is the current frame?
# used frame difference method



import cv2
import numpy as np


class ROIAnalyzer:

    def __init__(self, regions):

        self.regions = regions
        self.previous_frames = {}
        self.latest_metrics = []

    def analyze(self, frame):

        results = []

        for region in self.regions:

            frame_h, frame_w = frame.shape[:2]

            x = int( region["x"] * frame_w )
            y = int( region["y"] * frame_h )

            w = int( region["w"] * frame_w )
            h = int( region["h"] * frame_h )

            ## safety check ##
            x = max(0, x)
            y = max(0, y)

            w = min(w, frame_w - x)
            h = min(h, frame_h - y)




            roi = frame[y:y+h, x:x+w]

            name = region["name"]

            if roi.size == 0:
                continue

            # First frame
            if name not in self.previous_frames:

                self.previous_frames[name] = roi.copy()

                results.append({
                    "name": name,
                    "complexity": 0.0
                })

                continue

            previous_roi = self.previous_frames[name]

            diff = cv2.absdiff(
                roi,
                previous_roi
            )

            motion_score = float(
                np.mean(diff)
            )

            self.previous_frames[name] = roi.copy()

            results.append({

                "name": name,
                "complexity": round(
                    motion_score,
                    2
                )

            })

        self.latest_metrics = results

        return results






"""
def calculate_roi_complexity(
    video_path,
    roi
):
    cap = cv2.VideoCapture(video_path)

    prev_roi = None

    scores = []

    while True:

        ret, frame = cap.read()

        if not ret:
            break

        x = roi["x"]
        y = roi["y"]
        w = roi["w"]
        h = roi["h"]

        current_roi = frame[
            y:y+h,
            x:x+w
        ]

        gray = cv2.cvtColor(
            current_roi,
            cv2.COLOR_BGR2GRAY
        )

        if prev_roi is not None:

            diff = cv2.absdiff(
                gray,
                prev_roi
            )

            score = np.mean(diff) / 255

            scores.append(score)

        prev_roi = gray

    cap.release()

    if len(scores) == 0:
        return 0

    return np.mean(scores)
"""