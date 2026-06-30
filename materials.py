#!/usr/bin/env python3
"""
================================================================================
materials.py  -  spectroscopic & material property database
================================================================================
Every other engine has its own hard-coded constants (cross section, lifetime,
n2, dn/dT, ...). That's fine for reproducing one paper, but a platform needs a
SINGLE source of truth so you can swap the gain medium and have every engine
follow. This module is that database: a set of well-characterized laser
materials with the parameters the rest of LASERSIM consumes.

Included media
--------------
  Nd:YAG       - the paper's medium (1064 nm)
  Nd:glass     - broad bandwidth, big aperture, low conductivity
  Yb:YAG       - efficient, small quantum defect, thin-disk favourite
  Ti:Sapphire  - ultrabroad, fs systems

Each entry carries: lasing wavelength, emission cross section, upper-state
lifetime, saturation fluence, gain bandwidth, n2, dn/dT, thermal conductivity.

Run:
    python materials.py                 # list all media
    python materials.py --name Yb:YAG   # detail one medium
================================================================================
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass, asdict
from typing import Dict


@dataclass(frozen=True)
class Material:
    name: str
    lam_nm: float           # lasing wavelength
    sigma_m2: float         # stimulated-emission cross section [m^2]
    tau_us: float           # upper-state lifetime [us]
    f_sat_Jcm2: float       # saturation fluence [J/cm^2]
    bandwidth_nm: float     # gain bandwidth (FWHM)
    n0: float               # linear refractive index
    n2_cm2W: float          # nonlinear index [cm^2/W]
    dn_dT_perK: float       # thermo-optic coefficient [1/K]
    K_th_WmK: float         # thermal conductivity [W/(m K)]
    pump_nm: float          # typical pump wavelength

    @property
    def quantum_defect(self) -> float:
        """Fraction of pump photon energy lost as heat (1 - pump/lasing)."""
        return 1.0 - self.pump_nm / self.lam_nm


DATABASE: Dict[str, Material] = {
    "Nd:YAG": Material(
        name="Nd:YAG", lam_nm=1064.0, sigma_m2=2.8e-23, tau_us=230.0,
        f_sat_Jcm2=0.3, bandwidth_nm=0.6, n0=1.82, n2_cm2W=6.21e-16,
        dn_dT_perK=7.3e-6, K_th_WmK=14.0, pump_nm=808.0),
    "Nd:glass": Material(
        name="Nd:glass", lam_nm=1054.0, sigma_m2=4.0e-24, tau_us=350.0,
        f_sat_Jcm2=4.5, bandwidth_nm=22.0, n0=1.54, n2_cm2W=3.0e-16,
        dn_dT_perK=2.9e-6, K_th_WmK=1.0, pump_nm=802.0),
    "Yb:YAG": Material(
        name="Yb:YAG", lam_nm=1030.0, sigma_m2=2.1e-24, tau_us=950.0,
        f_sat_Jcm2=9.2, bandwidth_nm=9.0, n0=1.82, n2_cm2W=6.2e-16,
        dn_dT_perK=7.3e-6, K_th_WmK=11.0, pump_nm=940.0),
    "Ti:Sapphire": Material(
        name="Ti:Sapphire", lam_nm=800.0, sigma_m2=3.0e-23, tau_us=3.2,
        f_sat_Jcm2=0.9, bandwidth_nm=230.0, n0=1.76, n2_cm2W=3.2e-16,
        dn_dT_perK=13.0e-6, K_th_WmK=33.0, pump_nm=532.0),
}


def get(name: str) -> Material:
    if name not in DATABASE:
        raise KeyError(f"unknown material '{name}'. Known: {list(DATABASE)}")
    return DATABASE[name]


def to_cavity_kwargs(mat: Material) -> dict:
    """Map a Material onto laser_platform.Cavity constructor kwargs (SI)."""
    return dict(sigma=mat.sigma_m2, tau=mat.tau_us * 1e-6, n=mat.n0,
                lam=mat.lam_nm * 1e-9)


def main():
    ap = argparse.ArgumentParser(description="Laser material database")
    ap.add_argument("--name", help="show one material in detail")
    args = ap.parse_args()

    if args.name:
        m = get(args.name)
        print("=" * 56)
        print(f" {m.name}")
        print("=" * 56)
        for k, v in asdict(m).items():
            if k != "name":
                print(f"  {k:<16}: {v}")
        print(f"  {'quantum_defect':<16}: {m.quantum_defect*100:.1f} %")
        print("=" * 56)
        return

    print("=" * 72)
    print(" Laser material database")
    print("=" * 72)
    print(f"{'material':<14}{'lam':>7}{'tau(us)':>9}{'Fsat':>7}"
          f"{'BW(nm)':>8}{'K':>6}{'q-defect':>10}")
    print("-" * 72)
    for m in DATABASE.values():
        print(f"{m.name:<14}{m.lam_nm:>7.0f}{m.tau_us:>9.1f}{m.f_sat_Jcm2:>7.1f}"
              f"{m.bandwidth_nm:>8.1f}{m.K_th_WmK:>6.0f}{m.quantum_defect*100:>9.1f}%")
    print("=" * 72)
    print(" Use: from materials import get, to_cavity_kwargs")
    print("      from laser_platform import Cavity")
    print("      cav = Cavity(**to_cavity_kwargs(get('Yb:YAG')))")


if __name__ == "__main__":
    main()
