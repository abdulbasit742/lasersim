#!/usr/bin/env python3
"""
================================================================================
spatial_gain.py  -  2D spatially-resolved gain across a side-pumped laser rod
================================================================================
Real rods do NOT have uniform gain. In the NILOP 1.28 J Nd:YAG paper (Raza et
al., Opt. Commun. 577 (2025) 131413, Fig. 2), the side-pumped absorption is
peaked at the rod center (15 mm rods, GM1/GM2) and forms a ring/petal pattern in
the larger 25 mm rods (GM3/GM4). That non-uniform pump produces non-uniform
gain, which is exactly what degrades the super-Gaussian beam between stages.

This module builds a 2D pump-deposition map, converts it to a small-signal gain
map g0(x,y) = exp(F_store(x,y)/F_sat), then runs a *local* Frantz-Nodvik
extraction so you can see how a beam imprints the pump pattern onto its profile.

Run directly:
    python spatial_gain.py            # prints metrics, saves PNG if matplotlib
    python spatial_gain.py --module GM3
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
# PUMP DEPOSITION MODELS
# ==============================================================================
def pump_center_peaked(R, rod_radius, sharpness=1.4):
    """Center-peaked absorption (small 15 mm rods, GM1/GM2, Fig. 2a/b)."""
    g = np.exp(-(R / (sharpness * rod_radius)) ** 2)
    g[R > rod_radius] = 0.0
    return g


def pump_petal(R, THETA, rod_radius, n_petals=6, ring_frac=0.6, ring_w=0.22):
    """Ring/petal absorption (large 25 mm rods, GM3/GM4, Fig. 2c/d): pump enters
    from discrete diode bars around the circumference, leaving a structured
    azimuthal pattern with a brighter annulus."""
    ring = np.exp(-((R / rod_radius - ring_frac) / ring_w) ** 2)
    petals = 1.0 + 0.5 * np.cos(n_petals * THETA)
    g = ring * petals + 0.25 * np.exp(-(R / (0.9 * rod_radius)) ** 2)
    g[R > rod_radius] = 0.0
    return g / g.max()


# ==============================================================================
# ROD / MODULE
# ==============================================================================
@dataclass
class RodModule:
    name: str
    diameter_cm: float
    length_cm: float
    stored_energy_J: float
    f_sat: float = 0.3
    pump_kind: str = "center"   # "center" or "petal"

    @property
    def radius_cm(self):
        return self.diameter_cm / 2.0

    @property
    def area_cm2(self):
        return np.pi * self.radius_cm ** 2

    def grid(self, npix=301):
        x = np.linspace(-self.radius_cm, self.radius_cm, npix)
        X, Y = np.meshgrid(x, x)
        R = np.hypot(X, Y)
        THETA = np.arctan2(Y, X)
        return X, Y, R, THETA, x

    def pump_map(self, npix=301):
        _, _, R, THETA, _ = self.grid(npix)
        if self.pump_kind == "petal":
            return pump_petal(R, THETA, self.radius_cm)
        return pump_center_peaked(R, self.radius_cm)

    def stored_fluence_map(self, npix=301):
        """Distribute the measured stored energy according to the pump pattern,
        normalized so the integral matches stored_energy_J / area."""
        pmap = self.pump_map(npix)
        mask = pmap > 0
        mean_pump = pmap[mask].mean()
        f_store_avg = self.stored_energy_J / self.area_cm2
        return pmap / mean_pump * f_store_avg

    def gain_map(self, npix=301):
        """Small-signal gain g0(x,y) = exp(F_store / F_sat)."""
        fmap = self.stored_fluence_map(npix)
        return np.exp(fmap / self.f_sat)


# ==============================================================================
# LOCAL FRANTZ-NODVIK EXTRACTION
# ==============================================================================
def extract(rod: RodModule, beam_fluence_in: float, npix=301,
            beam_radius_cm=None, beam_order=4):
    """Push a super-Gaussian beam through the rod and apply local F-N extraction
    pixel by pixel. Returns (E_in, E_out, F_out_map, beam_in_map)."""
    X, Y, R, THETA, x = rod.grid(npix)
    br = beam_radius_cm or 0.75 * rod.radius_cm
    beam_in = np.exp(-2.0 * (R / br) ** beam_order)
    beam_in[R > rod.radius_cm] = 0.0
    F_in = beam_fluence_in * beam_in

    g0 = rod.gain_map(npix)
    F_out = rod.f_sat * np.log(1.0 + g0 * np.expm1(F_in / rod.f_sat))

    dA = (x[1] - x[0]) ** 2
    E_in = F_in.sum() * dA
    E_out = F_out.sum() * dA
    return E_in, E_out, F_out, beam_in


def beam_quality(profile: np.ndarray) -> float:
    """Crude flatness metric: 1.0 = perfectly flat top, ->0 = very peaked.
    Ratio of mean to peak over the illuminated region."""
    m = profile > 0.01 * profile.max()
    if not m.any():
        return 0.0
    return float(profile[m].mean() / profile.max())


# ==============================================================================
# BUILT-IN MODULES (from the paper)
# ==============================================================================
MODULES = {
    "GM1": RodModule("GM1", 1.5, 13.0, 1.622, pump_kind="center"),
    "GM2": RodModule("GM2", 1.5, 13.0, 1.622, pump_kind="center"),
    "GM3": RodModule("GM3", 2.5, 13.0, 1.14, pump_kind="petal"),
    "GM4": RodModule("GM4", 2.5, 13.0, 1.14, pump_kind="petal"),
}


def main():
    ap = argparse.ArgumentParser(description="Spatial gain map across a rod")
    ap.add_argument("--module", choices=sorted(MODULES), default="GM3")
    ap.add_argument("--fin", type=float, default=0.15,
                    help="input beam peak fluence [J/cm^2]")
    args = ap.parse_args()

    rod = MODULES[args.module]
    g0 = rod.gain_map()
    E_in, E_out, F_out, beam_in = extract(rod, args.fin)

    print("=" * 64)
    print(f" Spatial gain : {rod.name}  ({rod.diameter_cm*10:.0f} mm, {rod.pump_kind})")
    print("=" * 64)
    print(f"  avg stored fluence : {rod.stored_energy_J/rod.area_cm2:.3f} J/cm^2")
    print(f"  peak small-signal g0: {g0.max():.2f}")
    print(f"  input energy        : {E_in*1e3:.1f} mJ")
    print(f"  output energy       : {E_out*1e3:.1f} mJ  (gain {E_out/E_in:.2f}x)")
    print(f"  beam flatness in/out: {beam_quality(beam_in):.3f} -> {beam_quality(F_out):.3f}")
    print("=" * 64)

    if _HAVE_MPL:
        fig, ax = plt.subplots(1, 3, figsize=(14, 4.4))
        for a, data, title in zip(
            ax,
            [rod.pump_map(), g0, F_out],
            [f"{rod.name} pump deposition", "small-signal gain g0(x,y)",
             "amplified beam fluence out"],
        ):
            im = a.imshow(data, cmap="turbo",
                          extent=[-rod.radius_cm, rod.radius_cm,
                                  -rod.radius_cm, rod.radius_cm])
            a.set(title=title, xlabel="x [cm]", ylabel="y [cm]")
            fig.colorbar(im, ax=a, fraction=0.046)
        plt.tight_layout()
        out = f"spatial_gain_{rod.name}.png"
        plt.savefig(out, dpi=130)
        print(f"Saved -> {out}")
        plt.show()


if __name__ == "__main__":
    main()
