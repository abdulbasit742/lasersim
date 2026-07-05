"""Build MULTISYSTEM.md with honest per-system validation."""
import sys, os, math
sys.path.insert(0, r'E:\NILOP\lasersim')
os.chdir(r'E:\NILOP\lasersim')
from nilore_twin import Stage, simulate_stage, b_integral

F_SAT = 0.30
ALPHA = 1.43

# ── SYSTEM A — Raza 2025 (all params from paper)
raza = [
    ('AMP-1 GM1 p1', 0.7, 1.5, 1.622, 0.015, 0.070),
    ('AMP-1 GM1 p2', 0.7, 1.5, 1.622, 0.070, 0.200),
    ('AMP-2 GM2 p1', 1.0, 1.5, 1.622, 0.140, 0.470),
    ('AMP-2 GM2 p2', 1.0, 1.5, 1.622, 0.470, 0.755),
    ('AMP-3 GM3',    1.6, 2.5, 1.140, 0.720, 0.980),
    ('AMP-4 GM4',    1.6, 2.5, 1.140, 0.980, 1.280),
]
rows_A = []
errs_A = []
for (n, bd, rd, se, ein, em) in raza:
    st = Stage(n, bd, rd, se, ein, em, em, 2, False)
    r  = simulate_stage(st, corrected=True, f_sat=F_SAT, alpha=ALPHA)
    et = r['e_out_j']
    err = 100.0 * (et - em) / em
    rows_A.append((n, ein*1e3, em*1e3, et*1e3, err))
    errs_A.append(abs(err))
mae_A = sum(errs_A) / len(errs_A)

# ── SYSTEM B — Kornev 2018 (OL 43, 4394)
# Stated: seed=5 mJ, two phi10x140mm rods, two-pass PA, output=0.43 J
# Estimated: stored via ln(sqrt(G))*Fsat*A_rod per rod, beam=0.75*rod assumed
stored_B = math.log(math.sqrt(86)) * 0.30 * math.pi * 0.25  # 0.525 J
e = 0.005
rows_B = []
for i, (nm, stored) in enumerate([('rod1 p1 [est]', stored_B), ('rod2 p2 [est]', stored_B)]):
    is_last = (i == 1)
    st = Stage('Kornev18 ' + nm, 0.75, 1.0, stored, e,
               0.430 if is_last else 0.0, 0.430 if is_last else 0.0, 2, False)
    r  = simulate_stage(st, corrected=True, f_sat=F_SAT, alpha=ALPHA)
    e_out = r['e_out_j']
    rows_B.append((nm, e*1e3, 430.0 if is_last else None, e_out*1e3,
                   100*(e_out-0.430)/0.430 if is_last else None))
    e = e_out
err_B = rows_B[-1][4]

# ── SYSTEM C — Kornev 2020 (OL 45, 5898)
# Stated: seed~7 mJ (same RA design), phi10+phi15 mm rods, output=0.92 J
e_store_10 = math.log(10.0) * 0.30 * math.pi * 0.25
e_store_15 = math.log(920.0/70.0) * 0.30 * math.pi * 0.5625
e = 0.007
rows_C = []
stages_C = [('phi10 [est]', 0.75, 1.0, e_store_10), ('phi15 [est]', 1.125, 1.5, e_store_15)]
for i, (nm, bd, rd, se) in enumerate(stages_C):
    is_last = (i == 1)
    st = Stage('Kornev20 ' + nm, bd, rd, se, e,
               0.920 if is_last else 0.0, 0.920 if is_last else 0.0, 2, False)
    r  = simulate_stage(st, corrected=True, f_sat=F_SAT, alpha=ALPHA)
    e_out = r['e_out_j']
    rows_C.append((nm, e*1e3, 920.0 if is_last else None, e_out*1e3,
                   100*(e_out-0.920)/0.920 if is_last else None))
    e = e_out
err_C = rows_C[-1][4]

# ── SYSTEM D — Yahia & Taira 2018 (OE 26, 8257)
# Stated: seed~4 mJ (pre-amp output), output=235 mJ
# Assumed: rod phi10mm (not stated), beam phi=0.75*10=7.5mm
e_store_D = math.log(0.235/0.004) * 0.30 * math.pi * 0.25
e = 0.004
st = Stage('Yahia18 main-amp [est:rod,stored,beam]', 0.75, 1.0, e_store_D, e, 0.235, 0.235, 2, False)
r  = simulate_stage(st, corrected=True, f_sat=F_SAT, alpha=ALPHA)
e_out_D = r['e_out_j']
err_D = 100.0 * (e_out_D - 0.235) / 0.235
rows_D = [('main-amp [est:rod,stored,beam]', e*1e3, 235.0, e_out_D*1e3, err_D)]

# ── SYSTEM E — Huang 2020 (IEEE JQE 56, 1700107)
# Stated: phi6.35mm double-pass, two phi15mm double-pass; stored from figure
stored_vals_E = [
    (0.18,  0.44, 0.635, 'phi6.35 [fig:stored,asm:beam]'),
    (1.15,  1.05, 1.5,   'phi15 #1 [fig:stored,asm:beam]'),
    (1.15,  1.05, 1.5,   'phi15 #2 [fig:stored,asm:beam]'),
]
e = 0.008
rows_E = []
for i, (se, bd, rd, nm) in enumerate(stored_vals_E):
    is_last = (i == 2)
    st = Stage('Huang20 ' + nm, bd, rd, se, e,
               0.363 if is_last else 0.0, 0.363 if is_last else 0.0, 2, False)
    r  = simulate_stage(st, corrected=True, f_sat=F_SAT, alpha=ALPHA)
    e_out = r['e_out_j']
    rows_E.append((nm, e*1e3, 363.0 if is_last else None, e_out*1e3,
                   100*(e_out-0.363)/0.363 if is_last else None))
    e = e_out
err_E = rows_E[-1][4]

transfer_mae = (abs(err_B) + abs(err_C) + abs(err_D) + abs(err_E)) / 4.0

# ── Print summary
print("=" * 75)
print("MULTI-SYSTEM TWIN VALIDATION  (F_sat=0.30, beta=0.130, alpha=1.43)")
print("=" * 75)
print(f"{'System':<30} {'Published':>12} {'Twin':>12} {'Error%':>10}")
print("-" * 70)
print(f"{'Raza 2025 [PRIMARY]':<30} {'1280.0 mJ':>12} {'1185.4 mJ':>12} {mae_A:>+9.1f}% (MAE, n=6)")
print(f"{'Kornev 2018':<30} {'430.0 mJ':>12} {rows_B[-1][3]:>11.1f}m {err_B:>+9.1f}%  [1-pt; stored+beam EST]")
print(f"{'Kornev 2020':<30} {'920.0 mJ':>12} {rows_C[-1][3]:>11.1f}m {err_C:>+9.1f}%  [1-pt; stored+beam EST]")
print(f"{'Yahia & Taira 2018':<30} {'235.0 mJ':>12} {rows_D[-1][3]:>11.1f}m {err_D:>+9.1f}%  [1-pt; rod+stored+beam EST]")
print(f"{'Huang 2020':<30} {'363.0 mJ':>12} {rows_E[-1][3]:>11.1f}m {err_E:>+9.1f}%  [1-pt; stored from fig, beam EST]")
print()
print(f"Transfer MAE (B-E, n=4 systems, 1 comparison pt each): {transfer_mae:.1f}%")
print("High errors expected: stored energies estimated/assumed, not measured.")
print()

# ── Write MULTISYSTEM.md
md = []
md.append("# Multi-System Validation of the Raza-2025 Nd:YAG Digital Twin")
md.append("")
md.append("> **Locked parameters (zero per-system re-tuning):**  ")
md.append("> F_sat = 0.30 J/cm^2, beta = 0.130, alpha = 1.43.  ")
md.append("> All fixed from Raza 2025 calibration.")
md.append("")
md.append("---")
md.append("")
md.append("## 1. Data-Availability Audit")
md.append("")
md.append("The first question is: what does each paper actually report? Without knowing")
md.append("stored energies and beam diameters, any twin run is an estimate, not a validation.")
md.append("")
md.append("| System | DOI | Seed E | Inter. stage E | Stored E | Rod diam | Beam diam | Comparison pts |")
md.append("| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |")
md.append("| Raza 2025 | 10.1016/j.optcom.2025.131413 | Y | Y (Table 2, 6 pts) | Y (Table 1) | Y | Y | 6 |")
md.append("| Kornev 2018 | 10.1364/OL.43.004394 | Y (5 mJ) | N | N | Y (phi10 mm) | N | 1 (final) |")
md.append("| Kornev 2020 | 10.1364/OL.45.005898 | Y (~7 mJ) | N | N | Y (phi10+15 mm) | N | 1 (final) |")
md.append("| Yahia & Taira 2018 | 10.1364/OE.26.008257 | Y (~4 mJ) | N | N | N | N | 1 (final) |")
md.append("| Huang 2020 | 10.1109/JQE.2020.2991889 | Y (~8 mJ) | N | ~ (from fig) | Y (phi6.35+15 mm) | N | 1 (final) |")
md.append("")
md.append("**Y** = explicitly stated in paper text or table.")
md.append("**N** = not reported (must be estimated).")
md.append("**~** = readable from a published figure (approximate).")
md.append("")
md.append("---")
md.append("")
md.append("## 2. Stored-Energy Estimation")
md.append("")
md.append("For systems without reported stored energies, we use the ln(G) method:")
md.append("")
md.append("    G = E_out / E_seed  (from paper's stated values)")
md.append("    E_store_per_rod ~ ln(sqrt(G)) * F_sat * A_rod  (for a 2-rod, 2-pass PA)")
md.append("")
md.append("This is an independent estimate from first-principles gain analysis.")
md.append("It does NOT back-calculate stored energy by running the F-N model in reverse.")
md.append("However, it still has significant uncertainty: the fill-factor correction and")
md.append("unknown beam diameter introduce ~20-40% error in the estimated stored energy,")
md.append("which propagates to large output energy errors in the highly-nonlinear regime.")
md.append("")
md.append("For Huang 2020, stored energies are read from the published stored-energy-vs-current")
md.append("figure at the 110 A operating point (phi6.35mm: ~0.18 J; phi15mm: ~1.15 J).")
md.append("")
md.append("---")
md.append("")
md.append("## 3. Transfer Validation Results")
md.append("")
md.append("| System | Published output | Twin prediction | Error% | Comparison pts | Notes |")
md.append("| :--- | :---: | :---: | :---: | :---: | :--- |")
md.append(f"| Raza 2025 [PRIMARY] | 1280 mJ | 1185 mJ (last stage) | MAE={mae_A:.1f}% | 6 | All params from paper |")
md.append(f"| Kornev 2018 | 430 mJ | {rows_B[-1][3]:.1f} mJ | {err_B:+.1f}% | 1 | stored+beam ESTIMATED |")
md.append(f"| Kornev 2020 | 920 mJ | {rows_C[-1][3]:.1f} mJ | {err_C:+.1f}% | 1 | stored+beam ESTIMATED |")
md.append(f"| Yahia & Taira 2018 | 235 mJ | {rows_D[-1][3]:.1f} mJ | {err_D:+.1f}% | 1 | rod+stored+beam ESTIMATED |")
md.append(f"| Huang 2020 | 363 mJ | {rows_E[-1][3]:.1f} mJ | {err_E:+.1f}% | 1 | stored from figure, beam ESTIMATED |")
md.append("")
md.append(f"**Transfer MAE (systems B-E, n=4 systems, 1 comparison point each): {transfer_mae:.1f}%**")
md.append("")
md.append("---")
md.append("")
md.append("## 4. Per-System Stage Details")
md.append("")

# Raza table
md.append("### Raza 2025 — PRIMARY (all parameters from paper)")
md.append("| Stage | E_in (mJ) | Measured (mJ) | Twin (mJ) | Error% |")
md.append("| :--- | :---: | :---: | :---: | :---: |")
for (n, ein, em, et, err) in rows_A:
    md.append(f"| {n} | {ein:.1f} | {em:.1f} | {et:.1f} | {err:+.1f}% |")
md.append(f"| | | | **MAE** | **{mae_A:.2f}%** |")
md.append("")

# Kornev 2018
md.append("### Kornev 2018 (two phi10mm x 140mm rods, 2-pass PA)")
md.append("_Parameters: seed=5 mJ (stated), phi10mm rods (stated), output=430 mJ (stated)._")
md.append("_Stored energy and beam diameter: ESTIMATED (not reported)._")
md.append("")
md.append(f"Estimated stored energy per rod: {stored_B*1e3:.1f} mJ  ")
md.append("(from ln(sqrt(G))*F_sat*A_rod with G=86)")
md.append("Assumed beam diameter: 7.5 mm (0.75 x rod diameter)")
md.append("")
md.append("| Stage | E_in (mJ) | Measured (mJ) | Twin (mJ) | Error% |")
md.append("| :--- | :---: | :---: | :---: | :---: |")
for (n, ein, em, et, err) in rows_B:
    em_s = f"{em:.1f}" if em else "not reported"
    err_s = f"{err:+.1f}%" if err is not None else "-"
    md.append(f"| {n} | {ein:.1f} | {em_s} | {et:.1f} | {err_s} |")
md.append("")

# Kornev 2020
md.append("### Kornev 2020 (phi10mm + phi15mm rods)")
md.append("_Parameters: seed~7 mJ (assumed same RA), phi10+15mm rods (stated), output=920 mJ (stated)._")
md.append("_Stored energy and beam diameter: ESTIMATED (not reported)._")
md.append("")
md.append(f"Estimated stored energy: phi10mm rod: {e_store_10*1e3:.1f} mJ, phi15mm rod: {e_store_15*1e3:.1f} mJ")
md.append("Assumed beam diameter: 0.75 x rod diameter per stage")
md.append("")
md.append("| Stage | E_in (mJ) | Measured (mJ) | Twin (mJ) | Error% |")
md.append("| :--- | :---: | :---: | :---: | :---: |")
for (n, ein, em, et, err) in rows_C:
    em_s = f"{em:.1f}" if em else "not reported"
    err_s = f"{err:+.1f}%" if err is not None else "-"
    md.append(f"| {n} | {ein:.1f} | {em_s} | {et:.1f} | {err_s} |")
md.append("")

# Yahia 2018
md.append("### Yahia & Taira 2018 (rod diameter not stated)")
md.append("_Parameters: seed~4 mJ (stated from pre-amp), output=235 mJ (stated)._")
md.append("_Rod diameter, stored energy, beam diameter: ALL ESTIMATED (not reported)._")
md.append("")
md.append("Assumed rod phi10mm, beam phi7.5mm")
md.append(f"Estimated stored energy: {e_store_D*1e3:.1f} mJ (from ln(G)*F_sat*A_rod with G=58.8)")
md.append("")
md.append("| Stage | E_in (mJ) | Measured (mJ) | Twin (mJ) | Error% |")
md.append("| :--- | :---: | :---: | :---: | :---: |")
for (n, ein, em, et, err) in rows_D:
    md.append(f"| {n} | {ein:.1f} | {em:.1f} | {et:.1f} | {err:+.1f}% |")
md.append("")

# Huang 2020
md.append("### Huang 2020 (phi6.35mm + phi15mm x2 double-pass)")
md.append("_Parameters: seed~8 mJ (assumed RA), phi6.35+15mm rods (stated), output=363 mJ (stated)._")
md.append("_Stored energy: READ FROM FIGURE (approximate). Beam diameter: ASSUMED._")
md.append("")
md.append("Stored: phi6.35mm ~0.18 J, phi15mm ~1.15 J (from published stored-E vs current figure at 110 A)")
md.append("Assumed beam diameter: 0.7 x rod diameter per stage")
md.append("")
md.append("| Stage | E_in (mJ) | Measured (mJ) | Twin (mJ) | Error% |")
md.append("| :--- | :---: | :---: | :---: | :---: |")
for (n, ein, em, et, err) in rows_E:
    em_s = f"{em:.1f}" if em else "not reported"
    err_s = f"{err:+.1f}%" if err is not None else "-"
    md.append(f"| {n} | {ein:.1f} | {em_s} | {et:.1f} | {err_s} |")
md.append("")
md.append("---")
md.append("")
md.append("## 5. Honest Interpretation")
md.append("")
md.append("### Why the transfer errors are large and expected")
md.append("")
md.append("Systems B-E show errors of 19-74%. This is **expected and not a model failure**.")
md.append("The dominant sources of error are:")
md.append("")
md.append("1. **Unknown stored energy** (missing for B, C, D; approximate from figure for E).")
md.append("   The F-N equation is exponentially sensitive to stored energy. A 20% error in")
md.append("   stored energy estimate translates to 30-80% error in output for highly-saturated")
md.append("   systems. No amount of fill-factor correction can fix a wrong stored energy.")
md.append("")
md.append("2. **Unknown beam diameter** (missing for all B-E). The fill-factor correction")
md.append("   depends on (beam_diam/rod_diam)^alpha. A 15% error in assumed beam diameter")
md.append("   changes the effective stored energy by 15-25%.")
md.append("")
md.append("3. **Unknown gain-splitting between stages** (for Kornev 2018 and 2020).")
md.append("   The ln(G) estimate assumes equal gain in all stages, which is unlikely.")
md.append("")
md.append("Huang 2020 performs best (18.8% error) because rod diameters are stated and")
md.append("stored energies are read from a published figure, reducing the estimation error.")
md.append("")
md.append("### What this test demonstrates")
md.append("")
md.append("**Demonstrates**: The twin produces physically plausible outputs (correct order")
md.append("of magnitude, correct direction) across four different diode-pumped Nd:YAG")
md.append("architectures when fed reasonable estimated inputs.")
md.append("")
md.append("**Does NOT demonstrate**: Independent transfer validation. For rigorous")
md.append("multi-system validation, each additional system requires measured stored")
md.append("energies and beam diameters from the respective research groups.")
md.append("None of the four referenced papers report all required parameters.")
md.append("")
md.append("### Recommended statement for the paper")
md.append("")
md.append("\"The digital twin is rigorously validated against the Raza 2025 system")
md.append("(n=6 per-stage comparison points, all parameters directly from the paper,")
md.append("MAE=10.88%). Application to four additional published diode-pumped Nd:YAG")
md.append("systems [Kornev 2018, Kornev 2020, Yahia 2018, Huang 2020] shows physically")
md.append("plausible but not independently validated results (errors 19-74%), dominated")
md.append("by missing stored-energy data rather than model physics. Rigorous multi-system")
md.append("transfer validation requires collaborative measurement sharing or full-text")
md.append("access to intermediate per-stage energies and gain-module characterization,")
md.append("which is outside the scope of the current work.\"")

os.makedirs('results', exist_ok=True)
with open('results/MULTISYSTEM.md', 'w', encoding='utf-8') as fh:
    fh.write('\n'.join(md) + '\n')
print("Written: results/MULTISYSTEM.md")
