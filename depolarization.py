#!/usr/bin/env python3
"""
================================================================================
depolarization.py  -  thermally-induced birefringence & depolarization loss
================================================================================
A cylindrical rod under radial heat load develops radial and azimuthal stress.
Via the photoelastic effect this makes the rod BIREFRINGENT, and the principal
axes point radially/azimuthally (not along your linear polarization). A linearly
polarized beam therefore picks up a position-dependent polarization rotation,
and a polarizer downstream rejects part of it: this is DEPOLARIZATION LOSS. It
shows up as a characteristic 'Maltese cross' pattern and steals energy and beam
quality in high-average-power rods. The paper sidesteps much of it with circular
polarization, but the loss mechanism is fundamental and worth modeling.

Model
-----
  Thermally induced phase retardation grows ~ quadratically with radius and
  linearly with pump power:
      delta(r, phi) = C * P * (r/R)^2 * sin(2 phi)
  Depolarized fraction integrated over the aperture:
      eta_depol = < sin^2(2 phi) sin^2(delta/2) >  over the beam

Reports the depolarization loss vs pump power and how much a 90-degree quartz
rotator between two rods recovers.

Run:
    python depolarization.py
    python depolarization.py --power 200 --compensated
================================================================================
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass

import numpy as np

try:
    import matplotlib.pyplot as plt
    _HAVE_MPL = True
except Exception:
    _HAVE_MPL = False


@dataclass
class DepolRod:
    radius_m: float = 7.5e-3
    C_depol: float = 4.0e-4       # retardation per watt at the rim [rad/W]
    npix: int = 401

    def grids(self):
        x = np.linspace(-self.radius_m, self.radius_m, self.npix)
        X, Y = np.meshgrid(x, x)
        R = np.hypot(X, Y)
        PHI = np.arctan2(Y, X)
        return X, Y, R, PHI

    def retardation(self, P_W):
        X, Y, R, PHI = self.grids()
        delta = self.C_depol * P_W * (R / self.radius_m) ** 2
        return R, PHI, delta

    def depol_fraction(self, P_W, compensated=False):
        """Fraction of a linearly polarized beam converted to the orthogonal
        polarization (and thus lost at a clean-up polarizer)."""
        R, PHI, delta = self.retardation(P_W)
        mask = R <= self.radius_m
        if compensated:
            # a 90-deg rotator between two identical rods halves the net
            # retardation contribution (classic birefringence compensation)
            delta = delta / 2.0
        local = (np.sin(2 * PHI) ** 2) * (np.sin(delta / 2.0) ** 2)
        return float(local[mask].mean())


def main():
    ap = argparse.ArgumentParser(description="Thermal depolarization loss")
    ap.add_argument("--power", type=float, default=200.0, help="pump/heat power [W]")
    ap.add_argument("--compensated", action="store_true",
                    help="add a 90-deg rotator between two rods")
    args = ap.parse_args()

    rod = DepolRod()
    loss = rod.depol_fraction(args.power, args.compensated)
    loss_uncomp = rod.depol_fraction(args.power, False)

    print("=" * 60)
    print(" Thermally-induced depolarization loss")
    print("=" * 60)
    print(f"  pump/heat power     : {args.power:.0f} W")
    print(f"  depolarization loss : {loss*100:.2f} %"
          + ("  (compensated)" if args.compensated else ""))
    if args.compensated:
        print(f"  uncompensated would be: {loss_uncomp*100:.2f} %")
        print(f"  -> rotator recovers ~{(loss_uncomp-loss)/loss_uncomp*100:.0f}% of the loss")
    print("  note: circular polarization (paper's choice) avoids most of this.")
    print("=" * 60)

    if _HAVE_MPL:
        R, PHI, delta = rod.retardation(args.power)
        mask = R <= rod.radius_m
        pattern = (np.sin(2 * PHI) ** 2) * (np.sin(delta / 2.0) ** 2)
        pattern[~mask] = np.nan
        fig, ax = plt.subplots(1, 2, figsize=(11, 4.4))
        im = ax[0].imshow(pattern, cmap="inferno",
                          extent=[-rod.radius_m*1e3, rod.radius_m*1e3,
                                  -rod.radius_m*1e3, rod.radius_m*1e3])
        ax[0].set(title="Depolarization (Maltese cross)", xlabel="x [mm]", ylabel="y [mm]")
        fig.colorbar(im, ax=ax[0], fraction=0.046)
        Ps = np.linspace(10, 400, 100)
        ax[1].plot(Ps, [rod.depol_fraction(p)*100 for p in Ps], lw=2, label="uncompensated")
        ax[1].plot(Ps, [rod.depol_fraction(p, True)*100 for p in Ps], lw=2, label="compensated")
        ax[1].set(title="Depol. loss vs power", xlabel="power [W]", ylabel="loss [%]")
        ax[1].legend()
        plt.tight_layout(); plt.savefig("depolarization.png", dpi=130)
        print("Saved -> depolarization.png")
        plt.show()


if __name__ == "__main__":
    main()
