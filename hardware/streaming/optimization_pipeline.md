# Real-Time Beam Optimization Pipeline

## Pipeline

Camera Frame

→ Buffer Queue

→ Normalization / Preprocessing

→ TensorRT or CNN Inference

→ Beam Mode Prediction

## Goals

- low latency processing
- stable frame rate
- hardware independent camera layer
- future CUDA stream integration
