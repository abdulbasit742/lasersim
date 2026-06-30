#!/usr/bin/env python3
"""
================================================================================
dashboard.py  -  interactive web dashboard for the LASERSIM platform
================================================================================
A Streamlit front-end that puts every engine behind sliders so you can explore
the whole laser system in the browser, no code editing required.

Tabs
----
  * Oscillator : pick a rate-equation model, sweep pump/cavity, watch the
                 dynamics + threshold curve live.
  * Amplifier  : tune stored energy / beam size / passes, see energy + B-integral
                 against the paper's 1.28 J chain.
  * Thermal    : sweep pump power -> thermal lens, cavity stability, mode size.
  * Beam shape : serrated aperture + spatial filter, before/after profiles.
  * OPCPA      : drive the parametric front-end with this Nd:YAG pump.

Run:
    pip install streamlit
    streamlit run dashboard.py
================================================================================
"""
from __future__ import annotations

import numpy as np

try:
    import streamlit as st
except Exception:  # pragma: no cover
    raise SystemExit("Install streamlit first:  pip install streamlit")

import matplotlib.pyplot as plt

from laser_platform import (
    Cavity, MODEL_REGISTRY, FourLevelLaser, li_curve, QSwitchActive,
)
from amplifier import GainModule, AmplifierStage, build_nilop_amplifier
from thermal_abcd import ThermalRod, TwoMirrorCavity
from beam_shaping import run_pipeline
from opcpa import ChirpedPulse, OPACrystal, opa_gain_nondepleted, solve_depleted


st.set_page_config(page_title="LASERSIM", page_icon="\U0001F526", layout="wide")
st.title("\U0001F526 LASERSIM \u2014 laser modeling platform")
st.caption("Interactive front-end for the NILOP 1.28 J / 200 ps Nd:YAG system "
           "and its building blocks.")

tab_osc, tab_amp, tab_th, tab_bs, tab_opcpa = st.tabs(
    ["Oscillator", "Amplifier", "Thermal + cavity", "Beam shaping", "OPCPA"]
)

# ------------------------------------------------------------------ Oscillator
with tab_osc:
    c1, c2 = st.columns([1, 2])
    with c1:
        model_name = st.selectbox("Model", sorted(MODEL_REGISTRY), index=1)
        r2 = st.slider("Output coupler R2", 0.80, 0.99, 0.95, 0.01)
        pump_ratio = st.slider("Pump ratio r (xN_th)", 0.5, 10.0, 4.0, 0.1)
        cav0 = Cavity(R2=r2)
        cav = Cavity(R2=r2, Rp=pump_ratio * cav0.Rp_threshold)
        st.metric("Cavity photon lifetime", f"{cav.tau_c*1e9:.1f} ns")
        st.metric("Relaxation osc. freq", f"{cav.relaxation_freq_hz()/1e3:.1f} kHz")
    with c2:
        model = MODEL_REGISTRY[model_name](cav)
        model.n_pts = min(model.n_pts, 6000)
        res = model.simulate()
        fig, ax = plt.subplots(figsize=(7, 3.6))
        for lab in res.labels:
            y = res.series(lab)
            ax.plot(res.t * 1e6, y / (np.max(np.abs(y)) + 1e-30), lw=1, label=lab)
        ax.set(xlabel="t [us]", ylabel="normalized", title=model_name)
        ax.legend()
        st.pyplot(fig)
        rs, P = li_curve(cav0)
        fig2, ax2 = plt.subplots(figsize=(7, 2.8))
        ax2.plot(rs, P * 1e3, lw=2); ax2.axvline(1.0, color="r", ls="--")
        ax2.set(xlabel="pump ratio r", ylabel="P_out [mW]", title="L-I curve")
        st.pyplot(fig2)

# ------------------------------------------------------------------- Amplifier
with tab_amp:
    c1, c2 = st.columns([1, 2])
    with c1:
        e_store = st.slider("Stored energy / module [J]", 0.5, 2.0, 1.14, 0.05)
        beam_r = st.slider("Beam radius [cm]", 0.3, 1.5, 0.8, 0.05)
        passes = st.selectbox("Passes", [1, 2], index=0)
        gm = GainModule("X", 2.5, 13.0, e_store)
        stage = AmplifierStage("X", [gm, gm] if passes == 1 else [gm],
                               passes=passes, beam_radius_cm=beam_r, beam_order_n=4)
        _, r = stage.run(0.72)
        st.metric("Output energy", f"{r.e_out_mJ:.0f} mJ")
        st.metric("Peak fluence", f"{r.peak_fluence:.2f} J/cm^2")
        b_color = "normal" if r.b_integral < 3 else "inverse"
        st.metric("B-integral", f"{r.b_integral:.2f} rad",
                  delta="SAFE" if r.b_integral < 3 else "RISK", delta_color=b_color)
    with c2:
        st.subheader("Full NILOP chain vs paper")
        results = build_nilop_amplifier().run()
        st.table([{"stage": x.name, "E_out (mJ)": round(x.e_out_mJ),
                   "gain": round(x.gain, 2), "B": round(x.b_integral, 2)}
                  for x in results])

# ------------------------------------------------------------------- Thermal
with tab_th:
    rod = ThermalRod()
    cav = TwoMirrorCavity(R1=np.inf, R2=5.0, d1=0.15, d2=0.15, rod=rod)
    Ps = np.linspace(20, 400, 80)
    f_th = np.array([rod.focal_length(P) for P in Ps]) * 100
    m = np.array([cav.stability(P) for P in Ps])
    fig, ax = plt.subplots(1, 2, figsize=(11, 3.6))
    ax[0].plot(Ps, f_th, lw=2); ax[0].set(xlabel="P_pump [W]", ylabel="f_th [cm]",
                                          title="Thermal lens")
    ax[1].plot(Ps, m, lw=2); ax[1].axhspan(-1, 1, color="g", alpha=0.15)
    ax[1].axhline(1, color="r", ls="--"); ax[1].axhline(-1, color="r", ls="--")
    ax[1].set(xlabel="P_pump [W]", ylabel="(A+D)/2", title="Cavity stability")
    st.pyplot(fig)

# ---------------------------------------------------------------- Beam shaping
with tab_bs:
    pin = st.slider("Pin-hole diameter [um]", 40, 200, 110, 5)
    grid, beam, sa, after_sa, after_sf, metrics = run_pipeline(pinhole_um=pin)
    cols = st.columns(4)
    for col, data, title in zip(cols, [beam, sa, after_sa, after_sf],
                                ["input", "serrated aperture", "after SA", "after SF"]):
        fig, ax = plt.subplots(figsize=(3, 3))
        ax.imshow(data, cmap="turbo"); ax.set_title(title); ax.axis("off")
        col.pyplot(fig)
    st.write({k: round(v, 3) for k, v in metrics.items()})

# ----------------------------------------------------------------------- OPCPA
with tab_opcpa:
    c1, c2 = st.columns([1, 2])
    with c1:
        I_pump = st.slider("Pump intensity [GW/cm^2]", 0.1, 10.0, 2.0, 0.1) * 1e9
        L = st.slider("Crystal length [mm]", 2.0, 30.0, 15.0, 1.0)
        crystal = OPACrystal(length_mm=L)
        g = crystal.kappa(I_pump)
        G = opa_gain_nondepleted(g, L)
        st.metric("Signal gain", f"{G:.2e}x")
        st.metric("Idler wavelength", f"{crystal.lam_idler_nm:.0f} nm")
    with c2:
        z, Ps, Pi, Pp = solve_depleted(g, L)
        fig, ax = plt.subplots(figsize=(7, 3.6))
        ax.plot(z * 1e3, Pp, label="pump", lw=2)
        ax.plot(z * 1e3, Ps, label="signal", lw=2)
        ax.plot(z * 1e3, Pi, label="idler", lw=2, ls="--")
        ax.set(xlabel="z [mm]", ylabel="normalized power", title="3-wave OPA")
        ax.legend()
        st.pyplot(fig)
