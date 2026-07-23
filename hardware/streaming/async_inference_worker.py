"""Asynchronous inference worker foundation for real-time beam streaming."""

import queue
import threading


class AsyncInferenceWorker:
    def __init__(self, predictor, max_queue_size=4):
        self.predictor = predictor
        self.frames = queue.Queue(maxsize=max_queue_size)
        self.running = False
        self.thread = None
        self.latest_result = None

    def submit(self, frame):
        if not self.frames.full():
            self.frames.put(frame)

    def _loop(self):
        while self.running:
            try:
                frame = self.frames.get(timeout=0.1)
                self.latest_result = self.predictor(frame)
            except queue.Empty:
                continue

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False
