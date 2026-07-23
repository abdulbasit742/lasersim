# GPU Inference Guide

## Purpose

Enable NVIDIA GPU acceleration for K-mode beam inference.

## Components

- NVIDIA GPU node labels
- Kubernetes GPU resource requests
- Runtime configuration
- Future CUDA optimization

## Deployment Flow

GPU Node -> Kubernetes Pod -> K-mode API -> Beam Prediction
