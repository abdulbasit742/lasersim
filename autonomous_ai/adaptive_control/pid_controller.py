"""PID controller foundation for adaptive laser beam stabilization."""

class PIDController:
    def __init__(self, kp=1.0, ki=0.0, kd=0.0):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.integral = 0.0
        self.previous_error = 0.0

    def update(self, target, measurement):
        error = target - measurement
        self.integral += error
        derivative = error - self.previous_error
        self.previous_error = error
        return (self.kp * error) + (self.ki * self.integral) + (self.kd * derivative)
