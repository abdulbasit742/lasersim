#!/usr/bin/env python3
"""
================================================================================
beam_shaping.py  -  serrated-aperture apodization + Fourier spatial filtering
================================================================================
In the NILOP 1.28 J Nd:YAG paper (Raza et al., Opt. Commun. 577 (2025) 131413,
Fig. 3), the beam between amplifier stages is cleaned in two steps:

  1. A SERRATED APERTURE (SA): a hard aperture whose edge is cut into ~100 saw-
     tooth teeth. The serration softens the transmission edge so the beam is
     apodized (smooth roll-off) instead of hard-clipped, which suppresses the
     high-frequency diffraction rings a hard edge would create. SA in the paper:
     outer/inner serration dia 8 mm / 6 mm, 100 teeth, ~20% energy clipped.

  2. A SPATIAL FILTER (SF): a relay telescope with a pin-hole at the Fourier
     plane. The pin-hole is a low-pass filter that removes the high-spatial-
     frequency content (diffraction ripple, hot spots) and restores a clean
     super-Gaussian. Paper: 70-130 um pin-holes, ~88% transmission.

This module simulates both on a 2D field using FFT-based Fraunhofer propagation.

Run directly:
    python beam_shaping.py            # full SA + SF pipeline, saves PNG
    python beam_shaping.py --pinhole 110
================================================================================
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from typing import Tuple

import numpy as np

try:
    import matplotlib.pyplot as plt
    _HAVE_MPL = True
except Exception:
    _HAVE_MPL = False


# ==============================================================================
# GRID
# ==============================================================================
@dataclass
class Grid:
    npix: int = 512
    window_mm: float = 20.0   # physical size of the simulation window

    def axes(self):
        x = np.linspace(-self.window_mm / 2, self.window_mm / 2, self.npix)
        X, Y = np.meshgrid(x, x)
        R = np.hypot(X, Y)
        TH = np.arctan2(Y, X)
        return X, Y, R, TH, x

    @property
    def dx_mm(self):
        return self.window_mm / self.npix


# ==============================================================================
# BEAMS
# ==============================================================================
def super_gaussian(R, w_mm, order=2):
    return np.exp(-((R / w_mm) ** order))


def add_hotspots(field, R, TH, strength=0.35, n=6):
    """Add a non-uniform petal/hot-spot modulation, as comes out of a real
    side-pumped rod, so we have something dirty to clean."""
    mod = 1.0 + strength * np.cos(n * TH) * np.exp(-(R / (R.max() * 0.5)) ** 2)
    return field * mod


# ==============================================================================
# SERRATED APERTURE
# ==============================================================================
def serrated_aperture(R, TH, r_inner_mm, r_outer_mm, n_teeth=100):
    """Transmission mask of a serrated aperture. Inside r_inner -> full pass;
    outside r_outer -> blocked; in between, the local cut radius oscillates with
    angle (the saw-teeth), giving a soft, angularly-averaged apodized edge."""
    tooth = 0.5 * (1.0 + np.cos(n_teeth * TH))            # 0..1 saw-tooth-ish
    edge_r = r_inner_mm + (r_outer_mm - r_inner_mm) * tooth
    T = np.clip((edge_r - R) / (r_outer_mm - r_inner_mm), 0.0, 1.0)
    T[R <= r_inner_mm] = 1.0
    T[R >= r_outer_mm] = 0.0
    return T


# ==============================================================================
# FOURIER SPATIAL FILTER (pin-hole at the focal plane)
# ==============================================================================
def spatial_filter(field, grid: Grid, pinhole_um: float, focal_mm: float = 400.0,
                   lam_nm: float = 1064.0):
    """Low-pass filter: FFT to the focal plane, apply a circular pin-hole, then
    inverse FFT back. Pin-hole radius in the focal plane is converted to a
    cutoff in spatial-frequency space via r_focal = lam * f * f_spatial."""
    F = np.fft.fftshift(np.fft.fft2(field))
    n = grid.npix
    fx = np.fft.fftshift(np.fft.fftfreq(n, d=grid.dx_mm * 1e-3))  # cycles/m
    FX, FY = np.meshgrid(fx, fx)
    FR = np.hypot(FX, FY)
    lam_m = lam_nm * 1e-9
    f_m = focal_mm * 1e-3
    # pin-hole physical radius -> max passed spatial frequency
    r_pin_m = (pinhole_um * 1e-6) / 2.0
    f_cut = r_pin_m / (lam_m * f_m)        # cycles/m
    mask = (FR <= f_cut).astype(float)
    out = np.fft.ifft2(np.fft.ifftshift(F * mask))
    return np.abs(out)


# ==============================================================================
# METRICS
# ==============================================================================
def energy(field, grid: Grid):
    return float((field ** 2).sum() * grid.dx_mm ** 2)


def flatness(field):
    m = field > 0.05 * field.max()
    return float(field[m].mean() / field.max()) if m.any() else 0.0


def modulation_depth(field):
    """Peak-to-mean ripple in the bright core (lower is cleaner)."""
    m = field > 0.5 * field.max()
    if not m.any():
        return 0.0
    core = field[m]
    return float((core.max() - core.min()) / (core.max() + core.min()))


# ==============================================================================
# PIPELINE
# ==============================================================================
def run_pipeline(pinhole_um=110.0, r_inner=3.0, r_outer=4.0):
    grid = Grid(npix=512, window_mm=20.0)
    X, Y, R, TH, x = grid.axes()

    # dirty input beam: super-Gaussian + petal hot spots
    beam = super_gaussian(R, w_mm=4.0, order=4)
    beam = add_hotspots(beam, R, TH)

    sa = serrated_aperture(R, TH, r_inner, r_outer)
    after_sa = beam * sa
    after_sf = spatial_filter(after_sa, grid, pinhole_um)

    e0 = energy(beam, grid)
    metrics = {
        "SA_transmission": energy(after_sa, grid) / e0,
        "SF_transmission": energy(after_sf, grid) / max(energy(after_sa, grid), 1e-30),
        "flatness_in": flatness(beam),
        "flatness_out": flatness(after_sf),
        "ripple_in": modulation_depth(beam),
        "ripple_out": modulation_depth(after_sf),
    }
    return grid, beam, sa, after_sa, after_sf, metrics


def main():
    ap = argparse.ArgumentParser(description="Serrated aperture + spatial filter")
    ap.add_argument("--pinhole", type=float, default=110.0,
                    help="pin-hole diameter [um]")
    args = ap.parse_args()

    grid, beam, sa, after_sa, after_sf, m = run_pipeline(pinhole_um=args.pinhole)

    print("=" * 60)
    print(" Beam shaping: serrated aperture + spatial filter")
    print("=" * 60)
    print(f"  SA transmission : {m['SA_transmission']*100:5.1f} %  (paper ~80%)")
    print(f"  SF transmission : {m['SF_transmission']*100:5.1f} %  (paper ~88%)")
    print(f"  beam flatness   : {m['flatness_in']:.3f} -> {m['flatness_out']:.3f}")
    print(f"  core ripple     : {m['ripple_in']:.3f} -> {m['ripple_out']:.3f}")
    print("=" * 60)

    if _HAVE_MPL:
        fig, ax = plt.subplots(1, 4, figsize=(17, 4.2))
        for a, data, title in zip(
            ax,
            [beam, sa, after_sa, after_sf],
            ["dirty input beam", "serrated aperture", "after SA", "after spatial filter"],
        ):
            im = a.imshow(data, cmap="turbo",
                          extent=[-grid.window_mm/2, grid.window_mm/2,
                                  -grid.window_mm/2, grid.window_mm/2])
            a.set(title=title, xlabel="x [mm]", ylabel="y [mm]")
            fig.colorbar(im, ax=a, fraction=0.046)
        plt.tight_layout()
        plt.savefig("beam_shaping.png", dpi=130)
        print("Saved -> beam_shaping.png")
        plt.show()


if __name__ == "__main__":
    main()
