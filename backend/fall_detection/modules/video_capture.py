import cv2
import time


class VideoCapture:
    def __init__(self, src=0):
        self.cap       = cv2.VideoCapture(src)
        self.prev_time = time.time()
        self.fps       = 0

    def read(self):
        """
        Returns
        -------
        (ret, frame, fps)  where fps is the rolling single-frame estimate.
        """
        ret, frame = self.cap.read()
        curr_time  = time.time()
        if ret:
            elapsed   = curr_time - self.prev_time
            self.fps  = 1.0 / elapsed if elapsed > 0 else 0
            self.prev_time = curr_time
        return ret, frame, self.fps

    def release(self):
        self.cap.release()
        cv2.destroyAllWindows()
