"""Low-latency frame buffering foundation."""

from collections import deque


class FrameBuffer:
    def __init__(self, max_size=8):
        self.frames = deque(maxlen=max_size)

    def push(self, frame):
        self.frames.append(frame)

    def latest(self):
        return self.frames[-1] if self.frames else None

    def size(self):
        return len(self.frames)
