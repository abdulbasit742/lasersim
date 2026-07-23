# Async Real-Time Beam Pipeline

## Architecture

Camera Stream

↓

Frame Buffer

↓

Async Worker

↓

GPU Stream Processor

↓

TensorRT / CNN Inference

↓

Beam Mode Prediction

## Goals

- reduce latency
- avoid blocking camera capture
- prepare CUDA stream integration
- support high FPS beam analysis
