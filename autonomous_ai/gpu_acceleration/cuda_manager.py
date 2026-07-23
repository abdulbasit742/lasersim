"""CUDA/GPU acceleration management foundation for LaserSim."""

class CudaManager:
    def __init__(self):
        self.devices = []

    def register_device(self, device_name):
        self.devices.append(device_name)
        return True

    def available_devices(self):
        return self.devices
