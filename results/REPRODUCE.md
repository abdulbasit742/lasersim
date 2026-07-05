# Reproducibility Guide for the Nd:YAG Digital Twin MOPA MOPA MOPA MOPA MOPA MOPA MOPA

This guide explains how to set up the environment and run the pipeline to reproduce all the validations, neural surrogates, inverse designs, and figures.

---

## 1. Environment Setup

The pipeline runs in a Python 3.10+ environment. Follow these commands to set up the virtual environment and install dependencies:

```bash
# 1. Create a virtual environment
python -m venv venv

# 2. Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# 3. Install PyTorch with CUDA 12.4 support (adjust for your hardware)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124

# 4. Install other scientific computing and plotting dependencies
pip install numpy matplotlib scipy
```

---

## 2. Reproduction Commands

To run the complete pipeline and regenerate all validations, surrogates, inverse designs, and figures, run:

```bash
# Full publication-grade run (requires GPU, RTX A6000 recommended)
python run_paper.py --full

# Smoke run (fast CPU-only validation for CI/testing, runs in ~10 seconds)
python run_paper.py --smoke
```

---

## 3. Hardware & Runtime Expectation

*   **Hardware Used:** NVIDIA RTX A6000 GPU (48 GB GDDR6 VRAM, Ampere architecture), Intel Xeon CPU.
*   **Expected Runtime (Full Run):**
    *   Surrogate Net Training (300k samples, 150 epochs): ~220-250 seconds.
    *   Differentiable Inverse Design (16k population, 600 steps): ~8-12 seconds.
    *   Validations, Plots, and report generation: ~3 seconds.
    *   **Total Runtime:** ~4-5 minutes.
*   **Expected Runtime (Smoke Run):**
    *   **Total Runtime:** ~10-15 seconds.

---

## 4. Output Artifacts

All outputs land in the `results/` folder:

*   **Report & Drafts:**
    *   `results/NILORE_VALIDATION.md`: Full validation table, statistical comparison, SHG table, inverse design target vs verification, and robustness section.
    *   `results/PAPER_DRAFT.md`: 1-page structured paper draft (skeleton) for publication.
*   **Validation & SHG Plots:**
    *   `results/twin_parity.png`: Output energy parity plot (Measured vs Twin vs Paper calculated).
    *   `results/stage_error_bar.png`: Per-stage signed error percentage comparison.
    *   `results/shg_curve.png`: 532 nm green energy and efficiency conversion curve (coupled-wave SHG).
*   **Neural Surrogate Plots & Data:**
    *   `results/surrogate_learning_curve.png`: MLP training and validation loss curves.
    *   `results/surrogate_parity_energy.png`: MLP prediction parity plot on the test set.
    *   `results/surrogate_net.pt`: Trained PyTorch neural surrogate weights.
    *   `results/surrogate_net.json`: Training and R² validation statistics.
*   **Inverse Design Data:**
    *   `results/neural_inverse.json`: Gradient-optimized design parameters and physics checks.
