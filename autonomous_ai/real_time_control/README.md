# Real-Time Control Layer

LaserSim autonomous control timing and stability foundation.

Components:

- Control Scheduler: manages deterministic control cycles.
- Stability Manager: enforces safe tuning boundaries.

Flow:

AI Decision -> Scheduler -> Safety Check -> Beam Adjustment -> Feedback
