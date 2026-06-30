#!/usr/bin/env python3
"""
================================================================================
pump_diode.py  -  808 nm pump diode-bar model
================================================================================
Everything upstream of the rod starts at the pump diodes. The paper uses QCW
diode arrays delivering 16.22 kW peak at 120 A (GM1/GM2). Diode behaviour sets
how much pump light you get AND at what wavelength, and the wavelength matters:
Nd:YAG absorbs in a narrow band around 808 nm, so if the diode junction heats up
and its wavelength drifts off the absorption peak, the rod absorbs less and gain
drops. This module models that.

Model
-----
  Optical power:   P = eta_slope * (I - I_threshold)          (L-I curve)
  Wavelength:      lambda(T) = lambda0 + dlam/dT * (T - T0)   (~0.3 nm/K)
  Junction temp:   T = T_cool + R_th * P_dissipated
  Absorption:      A(lambda) = A0 * exp(-((lambda - 808)/sigma_abs)^2)
  Effective absorbed pump = P_optical * A(lambda)

Reports the L-I curve, the wavelength drift with current, and the absorbed-pump
penalty when the diode runs hot.

Run:
    python pump_diode.py
    python pump_diode.py --current 120
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
class DiodeBar:
    i_threshold_A: float = 10.0
    slope_W_per_A: float = 147.0      # ~16.22 kW at 120 A over the array
    lam0_nm: float = 808.0            # at reference temperature
    dlam_dT: float = 0.30             # nm/K junction wavelength drift
    T0_C: float = 25.0
    T_cool_C: float = 25.0
    R_th_K_per_W: float = 2.0e-4      # junction-to-coolant (per array)
    elec_eta: float = 0.5             # electrical-to-optical efficiency
    abs_peak_nm: float = 808.0        # Nd:YAG absorption peak
    abs_sigma_nm: float = 1.5         # absorption band width

    def optical_power(self, I_A: float) -> float:
        return max(self.slope_W_per_A * (I_A - self.i_threshold_A), 0.0)

    def junction_temp(self, I_A: float) -> float:
        P_opt = self.optical_power(I_A)
        P_elec = P_opt / self.elec_eta if self.elec_eta > 0 else 0.0
        P_diss = P_elec - P_opt
        return self.T_cool_C + self.R_th_K_per_W * P_diss

    def wavelength(self, I_A: float) -> float:
        T = self.junction_temp(I_A)
        return self.lam0_nm + self.dlam_dT * (T - self.T0_C)

    def absorption(self, lam_nm: float) -> float:
        return np.exp(-((lam_nm - self.abs_peak_nm) / self.abs_sigma_nm) ** 2)

    def absorbed_pump(self, I_A: float) -> float:
        return self.optical_power(I_A) * self.absorption(self.wavelength(I_A))


def main():
    ap = argparse.ArgumentParser(description="808 nm pump diode-bar model")
    ap.add_argument("--current", type=float, default=120.0)
    args = ap.parse_args()

    d = DiodeBar()
    I = args.current
    print("=" * 60)
    print(" 808 nm pump diode-bar model")
    print("=" * 60)
    print(f"  drive current       : {I:.0f} A")
    print(f"  optical power       : {d.optical_power(I)/1e3:.2f} kW")
    print(f"  junction temp       : {d.junction_temp(I):.1f} C")
    print(f"  emission wavelength : {d.wavelength(I):.2f} nm")
    print(f"  absorption fraction : {d.absorption(d.wavelength(I))*100:.1f} %")
    print(f"  absorbed pump       : {d.absorbed_pump(I)/1e3:.2f} kW")
    print(f"  (paper: 16.22 kW peak diode power at 120 A)")
    print("=" * 60)

    if _HAVE_MPL:
        Is = np.linspace(0, 140, 200)
        fig, ax = plt.subplots(1, 3, figsize=(15, 4.2))
        ax[0].plot(Is, [d.optical_power(i)/1e3 for i in Is], lw=2)
        ax[0].set(title="L-I curve", xlabel="current [A]", ylabel="optical power [kW]")
        ax[1].plot(Is, [d.wavelength(i) for i in Is], lw=2, color="tab:red")
        ax[1].axhline(808, color="gray", ls="--", label="abs. peak")
        ax[1].set(title="Wavelength drift", xlabel="current [A]", ylabel="lambda [nm]")
        ax[1].legend()
        ax[2].plot(Is, [d.absorbed_pump(i)/1e3 for i in Is], lw=2, color="tab:green")
        ax[2].set(title="Absorbed pump power", xlabel="current [A]", ylabel="absorbed [kW]")
        plt.tight_layout(); plt.savefig("pump_diode.png", dpi=130)
        print("Saved -> pump_diode.png")
        plt.show()


if __name__ == "__main__":
    main()
