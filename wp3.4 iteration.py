import math
import sys

# ----------------------------------------------------------------------------------------------
# constants and unit conversions
KG2LB = 2.20462262
M2FT = 3.280839895
M22FT2 = 10.7639104
M32GAL = 264.172052
M32FT3 = 35.3146667
PA2PSF = 0.0208854342
KPA2PSI = 0.145037738
M2IN = 39.3700787
G = 9.81
RHO0 = 1.225
A0 = 340.294
T0 = 288.15
P0 = 101325.0
FTMIN2MS = 0.3048 / 60.0

# ----------------------------------------------------------------------------------------------
# INPUTS.  value / unit / source.   None = missing
# ----------------------------------------------------------------------------------------------
INPUTS = {
    # ---- top level / WP1 ----
    "mtom_0":        (8660.965,  "kg",    "WP1 final MTOM (start of the iteration)"),
    "oem_classI":    (5283.19,   "kg",    "WP1 Class I OEM (0.61 MTOM)"),
    "payload":       (1010.0,    "kg",    "Top-level requirement"),
    "fuel_mass_0":   (2367.78,   "kg",    "REQ-PROP-11 (= 0.2734 MTOM); used for the tank volume scaling"),
    "ldg_mass_frac": (0.88,      "-",     "WP1 landing mass / MTOM"),
    "M_cr":          (0.68,      "-",     "Top-level requirement"),
    "h_cr":          (12496.8,   "m",     "41,000 ft"),
    "ws_0":          (2200.0,    "N/m2",  "WP1 design point (first guess of W/S)"),
    "tw_0":          (0.232,     "-",     "WP1 design point (T/W)"),
    # ---- Class I fuel fraction (WP1 section 3.4.2 / C.2): Breguet ----
    "range_design":  (6100.0,    "km",    "Harmonic range = critical mission (WP1 3.4.4)"),
    "range_aux":      (1319.79,   "km",    "Auxiliary range R_x (WP1 C.1)"),
    "eta_tot":        (0.37,      "-",     "eta_eng * eta_p (WP1 3.4.2)"),
    "ld_classI":      (14.0,      "-",     "Class I lift-to-drag ratio (WP1 3.4.2)"),
    "e_fuel":         (44.0e6,    "J/kg",  "Heating value of kerosene (WP1 3.4.2)"),
    "ld_mode":        ("polar",   "-",     "'polar' = L/D from the Class II polar (default). 'classI' = L/D 14 and the WP1 drag polar"),
    # ---- wing (WP2 final) ----
    "AR":            (8.59,      "-",     "WP2 section 5.2.4"),
    "taper":         (0.363,     "-",     "WP2 (note: reader Eq 2.3 gives 0.400, unresolved)"),
    "sweep_c4":      (10.564,    "deg",   "WP2 quarter-chord sweep"),
    "tc_wing":       (0.14,      "-",     "SC(2)-0414"),
    "CLmax_clean":   (1.717,     "-",     "WP2.2 (WP1 matching diagram assumed 1.6)"),
    "CLmax_TO":      (1.8,       "-",     "WP1 assumption (flap design WP2.3)"),
    "CLmax_L":       (2.3,       "-",     "WP2.3 design target for the Fowler flap"),
    "wing_fuel_frac": (1.0,      "-",     "WP2.2: wing box volume > required, all fuel in the wing"),
    "fuel_volume":   (4.115,     "m3",    "WP2.2 required wing fuel volume (sized with 2927 kg fuel, 1.1 margin)"),
    "fuel_density":  (775.0,     "kg/m3", "WP2 section 2.5.2"),
    "tank_margin":   (1.1,       "-",     "WP2 section 2.5.2 safety factor"),
    "scale_fuel_volume": (True,  "-",     "scale tank volume with fuel mass during the iteration"),
    "N_tanks":       (2,         "-",     "ASSUMED: one integral tank per semi-span (WP2.2 wing-box model)"),
    # ---- fuselage (WP3.1) ----
    "L_fus":         (15.51,     "m",     "WP3.1 3.1.4. Fuselage length 15.51 m confirmed (the WP3.2 drag section uses 27.3 m = double counted cones)"),
    "d_fus_inner":   (2.358,     "m",     "WP3.1 3.1.3"),
    "d_fus_outer":   (2.438,     "m",     "WP3.1 3.1.3"),
    "S_wet_fus":     (94.65,     "m2",    "WP3.1 3.1.4"),
    "p_cabin":       (81.2,      "kPa",   "REQ-FUSE-01"),
    "p_ambient":     (17.87,     "kPa",   "REQ-FUSE-01"),
    "l_nose_cone":   (4.72,      "m",     "WP3.1 Table 3.4"),
    "l_cabin":       (5.4,       "m",     "WP3.1 3.1.4"),
    "l_cargo":       (1.66,      "m",     "WP3.1 3.1.3"),
    # ---- empennage (WP3.2 section 3.3: tail volume method, T-tail) ----
    "T_tail":        (True,      "-",     "T-tail selected (WP3.2 3.2.3): Ht/Hv = 1"),
    "V_H":           (0.75,      "-",     "WP3.2 3.3 horizontal tail volume coefficient"),
    "V_V":           (0.076,     "-",     "WP3.2 3.3 vertical tail volume coefficient"),
    "x_tail_frac":   (0.90,      "-",     "WP3.2 3.3: tail aerodynamic centre at 0.9 L_fus = 13.959 m"),
    "x_cg_frac":     (0.48,      "-",     "x_CG = 0.48 L_fus = 7.4448 m from the nose (team decision) -> tail arm 6.5142 m. (WP3.2 3.4.4 finds 8.937 m: not used)"),
    "tail_term_reading": ("wing", "-",    "Raymer 15.47/15.48 symbols A, t/c, Lambda: 'wing' or 'tail' (confirm with TA)"),
    # ---- propulsion (WP3.1) ----
    "N_eng":         (2,         "-",     "Two engines"),
    "m_engine":      (304.0,     "kg",    "FJ44-4A dry mass each"),
    "T_engine":      (16.10,     "kN",    "FJ44-4A sea-level static thrust each"),
    # ---- systems ----
    "m_avionics_uninstalled": (800.0 / KG2LB, "kg", "800 lb = low end of Raymer's typical range 800-1400 lb (small jet; not verified, argue with TA)"),
    "N_occupants":   (12,        "-",     "10 passengers + 2 pilots (REQ-FUSE-03)"),
    "ops_items_frac": (0.0,      "-",     "0 = pure Raymer (empty weight only). Lecture slides: operational items incl. crew 5-10 % of MTOM"),
    "trapped_frac":  (0.0,       "-",     "0 = pure Raymer. Lecture slides: trapped fuel + oil 0.1-0.5 % of MTOM"),
    "fudge":         (1.0,       "-",     "Raymer Table 15.4: 1.0 conventional aluminium"),
    # ---- load factor (fixed, team decision; no V-n diagram) ----
    "n_limit":       (2.5,       "-",     "Limit load factor 2.5 = minimum of CS 25.337(b) (assumed)"),
    "n_safety":      (1.5,       "-",     "Safety factor: ultimate Nz = 1.5 x 2.5 = 3.75 (Raymer's Nz is the ultimate value). Use 1.0 if 2.5 is meant as Nz itself"),
    # ---- Class II drag (report WP3.3 section 4.1, Table 4.8): Cf, FF, IF per component ----
    "drag_class2":   (True,      "-",     "True = Class II drag rebuilt every pass. False = WP1 statistical polar (same as --ld=classI)"),
    "Cf_wing": (0.00267, "-", "Table 4.8 (held; depends only weakly on Re/MAC)"),  "FF_wing": (1.5842, "-", "Table 4.8"), "IF_wing": (1.25, "-", "Table 4.8"),
    "Cf_ht":   (0.00284, "-", "Table 4.8"),  "FF_ht":   (1.5842, "-", "Table 4.8"), "IF_ht":   (1.04, "-", "Table 4.8 (T-tail)"),
    "Cf_vt":   (0.00261, "-", "Table 4.8"),  "FF_vt":   (1.5842, "-", "Table 4.8"), "IF_vt":   (1.04, "-", "Table 4.8 (T-tail)"),
    "Cf_fus":  (0.00218, "-", "Table 4.8"),  "FF_fus":  (1.0676, "-", "Table 4.8"), "IF_fus":  (1.0,  "-", "Table 4.8"),
    "Cf_nac":  (0.00279, "-", "Table 4.8"),  "FF_nac":  (1.1172, "-", "Table 4.8"), "IF_nac":  (1.3,  "-", "Table 4.8"),
    "Cf_pyl":  (0.00279, "-", "Table 4.8"),  "FF_pyl":  (1.5842, "-", "Table 4.8"), "IF_pyl":  (1.1,  "-", "Table 4.8"),
    "Swet_fus_drag": (84.72, "m2", "Table 4.1 (eq 4.8 with L1 3.50, cylinder 7.06, L3 4.95, D 2.358). NOTE: the weight equation uses 94.65 (WP3.1)"),
    "Swet_nac":      (8.97,  "m2", "Table 4.1 (2 nacelles)"),
    "Swet_pyl":      (1.90,  "m2", "Table 4.1 (2 pylons)"),
    "Swet_factor":   (1.07 * 2.0, "-", "Swet = 1.07 * 2 * S_exposed-planform, eqs 4.2-4.4"),
    "CD_misc":       (0.00041, "-", "Wave drag increment, section 4.1.5"),
    # Oswald factors. The report gives NO new e. The clean value stays that of the WP1 matching diagram,
    # the flap / gear increments of the WP1 polar (Table B.1) are kept as they are (not covered by section 4.1).
    "e_clean":       (0.80782,   "-",     "[ASSUMED] WP1 Table B.1. WP2.4 / Table 5.1 give 0.5989: run --e=0.5989 to see the effect"),
    "e_TO":          (0.84682,   "-",     "[ASSUMED] WP1 Table B.1"),
    "e_L":           (0.89882,   "-",     "[ASSUMED] WP1 Table B.1"),
    # WP1 statistical polar: only used when drag_class2 is False; the increments (flaps, gear) are ALWAYS taken from it
    "CD0_clean":     (0.01486,   "-",     "WP1 Table B.1 cruise, gear retracted"),
    "CD0_TO_ret":    (0.02101,   "-",     "WP1 Table B.1 take-off flaps 15 deg, gear retracted"),
    "CD0_TO_ext":    (0.04101,   "-",     "WP1 Table B.1 take-off flaps, gear extended"),
    "CD0_L_ret":     (0.04560,   "-",     "WP1 Table B.1 landing flaps 35 deg, gear retracted"),
    "CD0_L_ext":     (0.06560,   "-",     "WP1 Table B.1 landing flaps, gear extended"),
    # ---- matching diagram requirements and assumptions (WP1 Table 4.1 and section 4.1.2) ----
    "md_beta_cruise": (0.95,     "-",     "WP1 Table 4.1"),
    "md_beta_climb":  (0.97,     "-",     "WP1 Table 4.1"),
    "md_beta_land":   (0.88,     "-",     "WP1 Table 4.1"),
    "md_beta_appr":   (0.89,     "-",     "WP1 Table 4.1"),
    "theta_break":    (1.07,     "-",     "WP1 Table 4.1"),
    "V_appr":         (70.0,     "m/s",   "WP1 Table 4.1 approach speed"),
    "LFL":            (620.0,    "m",     "REQ landing field length"),
    "CL_FL":          (0.45,     "-",     "CS-25 landing field length parameter (WP1 4.1.2)"),
    "TOFL":           (1250.0,   "m",     "REQ take-off field length"),
    "kT":             (0.85,     "-",     "WP1 4.1.2"),
    "h2":             (11.0,     "m",     "CS-25 obstacle height"),
    "dT_hot":         (13.25,    "K",     "ISA + 13.25 K"),
    "h_TO":           (500.0,    "m",     "Take-off altitude (hot and high)"),
    "climb_rate":     (3600.0 * FTMIN2MS, "m/s", "REQ-OPER-01 as written in WP1 (3600 ft/min). The reader says 3000 ft/min"),
    "ws_round":       (10.0,     "N/m2",  "Round the landing-limited W/S DOWN to this step (WP1 used 2200 from 2206)"),
    "tw_margin":      (0.006,    "-",     "Margin added to the minimum T/W (WP1: 0.232 chosen above 0.226)"),
    # ---- iteration ----
    "tol":           (0.001,     "-",     "Convergence on the relative change of MTOM, OEM and W/S"),
    "max_iter":      (50,        "-",     ""),
}

# WP3 values that do not exist yet. Used unless --strict. Everything here is a PLACEHOLDER, not a result.
TENTATIVE = {
    "sweep_ht":  (20.0, "deg", "ASSUMED from typical jet values (Vos reader); tail planform not designed yet"),
    "taper_ht":  (0.45, "-",   "ASSUMED from typical values (Vos reader); exponent -0.02: almost no effect"),
    "AR_ht":     (4.5,  "-",   "only used if tail_term_reading = 'tail'"),
    "tc_ht":     (0.10, "-",   "only used if tail_term_reading = 'tail'"),
    "sweep_vt":  (35.0, "deg", "ASSUMED from typical jet values (Vos reader); tail planform not designed yet"),
    "taper_vt":  (0.80, "-",   "ASSUMED: WP3.2 3.2.3 fin taper 'close to one' for a T-tail (Vos reader)"),
    "AR_vt":     (1.2,  "-",   "only used if tail_term_reading = 'tail'"),
    "tc_vt":     (0.10, "-",   "only used if tail_term_reading = 'tail'"),
    "N_gear":    (2.5,  "-",   "REQ-LAND-01a (2.5 g). Raymer: GA 3.0, commercial 2.7-3.0 (Table 11.5)"),
    "L_main":    (1.5, "m", "Main gear strut ~150 cm (RK). WP3.2 3.4.3 tail-strike height is 1.4583 m (minimum)"),
    "L_nose":    (1.5, "m", "ASSUMED equal to the main gear strut"),
    "V_pressurized": (None, "m3", "computed below from the WP3.1 fuselage lengths (cabin + cargo + half the nose cone)"),
}

AVIONICS_RANGE_KG = (800.0 / KG2LB, 1400.0 / KG2LB)   # Raymer 'typically 800-1400 lb'

CURVES = ["cruise", "climb", "cg119", "cg121a", "cg121b", "cg121c", "cg121d", "tofl"]
# Reference values of the WP1 matching diagram (Matching_Diagram_Reference_Values.xlsx), AR = 8.8, CLmax clean 1.6
WP1_REF = {
    500: dict(zip(CURVES, [0.694752, 0.423739, 0.118133, 0.166574, 0.166653, 0.126097, 0.189006, 0.14817])),
    1000: dict(zip(CURVES, [0.370329, 0.311491, 0.117678, 0.165739, 0.165488, 0.125025, 0.188133, 0.178044])),
    2200: dict(zip(CURVES, [0.221748, 0.221471, 0.116595, 0.163757, 0.162735, 0.122501, 0.186061, 0.22622])),
    4000: dict(zip(CURVES, [0.207345, 0.171415, 0.114995, 0.160841, 0.158714, 0.118835, 0.183006, 0.275733])),
    8000: dict(zip(CURVES, [0.287294, 0.126215, 0.111539, 0.154595, 0.150226, 0.111182, 0.176446, 0.349486])),
}


# ----------------------------------------------------------------------------------------------
# atmosphere and thrust lapse
def isa(h, dT=0.0):
    if h <= 11000.0:
        T = 288.15 - 0.0065 * h
        p = 101325.0 * (T / 288.15) ** 5.25588
    else:
        T = 216.65
        p = 22632.06 * math.exp(-9.80665 * (h - 11000.0) / (287.058 * 216.65))
    T = T + dT
    rho = p / (287.058 * T)
    return T, p, rho, math.sqrt(1.4 * 287.058 * T)


def q_cruise(cfg):
    _, p, _, _ = isa(cfg["h_cr"])
    return 0.5 * 1.4 * p * cfg["M_cr"] ** 2  # Pa


def lapse(M, T_amb, p_amb, theta_break):
    """Thrust lapse alpha_T of WP1 section 4.1.2 (theta_t, delta_t from total temperature and pressure)."""
    ram = 1.0 + 0.2 * M * M
    theta = (T_amb / T0) * ram
    delta = (p_amb / P0) * ram ** 3.5
    if theta <= theta_break:
        return delta
    return delta * (1.0 - 2.1 * (theta - theta_break) / theta)


# ----------------------------------------------------------------------------------------------
# MATCHING DIAGRAM (WP1 section 4.1.2).  p = dict with the diagram inputs (see md_params)
def md_params(cfg, **over):
    p = dict(
        AR=cfg["AR"], N_eng=cfg["N_eng"], theta_break=cfg["theta_break"],
        CLmax_clean=cfg["CLmax_clean"], CLmax_TO=cfg["CLmax_TO"], CLmax_L=cfg["CLmax_L"],
        CD0_clean=cfg["CD0_clean"], e_clean=cfg["e_clean"],
        CD0_TO_ret=cfg["CD0_TO_ret"], CD0_TO_ext=cfg["CD0_TO_ext"], e_TO=cfg["e_TO"],
        CD0_L_ret=cfg["CD0_L_ret"], CD0_L_ext=cfg["CD0_L_ext"], e_L=cfg["e_L"],
        beta_cruise=cfg["md_beta_cruise"], beta_climb=cfg["md_beta_climb"],
        beta_land=cfg["md_beta_land"], beta_appr=cfg["md_beta_appr"],
        V_appr=cfg["V_appr"], LFL=cfg["LFL"], CL_FL=cfg["CL_FL"], TOFL=cfg["TOFL"], kT=cfg["kT"], h2=cfg["h2"],
        dT_hot=cfg["dT_hot"], h_TO=cfg["h_TO"], climb_rate=cfg["climb_rate"],
        h_cr=cfg["h_cr"], M_cr=cfg["M_cr"],
    )
    p.update(over)
    return p


def tw_curves(ws, p):
    """Required T_TO/W_TO of every constraint curve at wing loading ws [N/m2]."""
    A = p["AR"]
    thb = p["theta_break"]
    Ne = p["N_eng"]
    out = {}
    # --- cruise speed
    T, pa, rho, a = isa(p["h_cr"])
    V = p["M_cr"] * a
    q = 0.5 * rho * V * V
    al = lapse(p["M_cr"], T, pa, thb)
    out["cruise"] = (p["beta_cruise"] / al) * (p["CD0_clean"] * q / ws + ws / (math.pi * A * p["e_clean"] * q))
    # --- climb rate (sea level), flight at C_L = sqrt(CD0 pi A e)
    cd0, e = p["CD0_clean"], p["e_clean"]
    CL = math.sqrt(cd0 * math.pi * A * e)
    b = p["beta_climb"]
    V = math.sqrt(2.0 * b * ws / (RHO0 * CL))
    al = lapse(V / A0, T0, P0, thb)
    out["climb"] = (b / al) * (p["climb_rate"] / V + 2.0 * math.sqrt(cd0 / (math.pi * A * e)))
    # --- climb gradients  T/W = Ne/(Ne-1) * beta/alpha * (G + 2 sqrt(CD0/(pi A e)))
    #     speed rule k*V_stall (stall speed of the clean wing) FITTED to the WP1 reference table, see --validate
    spec = {
        "cg119":  dict(G=0.032, N=1, cd0=p["CD0_L_ext"], e=p["e_L"],  beta=p["beta_land"], k=1.2),
        "cg121a": dict(G=0.000, N=2, cd0=p["CD0_TO_ext"], e=p["e_TO"], beta=1.0, k=1.3),
        "cg121b": dict(G=0.024, N=2, cd0=p["CD0_TO_ret"], e=p["e_TO"], beta=1.0, k=1.4),
        "cg121c": dict(G=0.012, N=2, cd0=p["CD0_clean"], e=p["e_clean"], beta=1.0, k=1.4),
        "cg121d": dict(G=0.021, N=2, cd0=p["CD0_L_ret"], e=p["e_L"],  beta=p["beta_appr"], k=1.3),
    }
    for name, s in spec.items():
        Vs = math.sqrt(2.0 * s["beta"] * ws / (RHO0 * p["CLmax_clean"]))
        al = lapse(s["k"] * Vs / A0, T0, P0, thb)
        fac = (Ne / (Ne - 1.0)) if s["N"] == 2 else 1.0
        out[name] = fac * (s["beta"] / al) * (s["G"] + 2.0 * math.sqrt(s["cd0"] / (math.pi * A * s["e"])))
    # --- take-off field length, hot and high, V = 1.13 V_stall(take-off flaps), beta = 1
    Th, ph, rhoh, ah = isa(p["h_TO"], p["dT_hot"])
    ph = isa(p["h_TO"])[1]
    rhoh = ph / (287.058 * Th)
    Vs = math.sqrt(2.0 * ws / (rhoh * p["CLmax_TO"]))
    al = lapse(1.13 * Vs / ah, Th, ph, thb)
    N = Ne / (Ne - 1.0)
    out["tofl"] = (1.0 / al) * (1.15 * math.sqrt(N * ws / (p["TOFL"] * p["kT"] * rhoh * G * math.pi * A * p["e_TO"]))
                                + N * 4.0 * p["h2"] / p["TOFL"])
    return out


def ws_limits(p):
    """Vertical-line constraints: landing field length and approach speed (W_TO/S)."""
    land = (1.0 / p["beta_land"]) * (RHO0 / 2.0) * (p["CLmax_L"] / p["CL_FL"]) * p["LFL"]
    appr = (1.0 / p["beta_appr"]) * (RHO0 / 2.0) * (p["V_appr"] / 1.23) ** 2 * p["CLmax_L"]
    return {"landing field length": land, "approach speed": appr}


def design_point(cfg, **over):
    """Design point: highest W/S allowed by the vertical constraints, minimum T/W there (+ margin)."""
    p = md_params(cfg, **over)
    lim = ws_limits(p)
    key = min(lim, key=lim.get)
    ws_max = lim[key]
    step = cfg["ws_round"]
    ws = math.floor(ws_max / step) * step if step else ws_max
    cur = tw_curves(ws, p)
    crit = max(cur, key=cur.get)
    return dict(ws=ws, ws_max=ws_max, ws_limit_by=key, tw_min=cur[crit], tw_crit=crit,
                tw=cur[crit] + cfg["tw_margin"], curves=cur, limits=lim)


def validate_matching(cfg):
    """Reproduce the WP1 diagram (AR 8.8, CLmax clean 1.6) and compare with the reference table."""
    p = md_params(cfg, AR=8.8, CLmax_clean=1.6)
    print("=" * 96)
    print("VALIDATION OF THE MATCHING DIAGRAM AGAINST THE WP1 REFERENCE TABLE (AR = 8.8, CLmax clean = 1.6)")
    print("=" * 96)
    print(f"{'curve':8s}" + "".join(f"{w:>10d}" for w in WP1_REF) + f"{'max |err|':>12s}")
    worst = {}
    for c in CURVES:
        errs = []
        for w, ref in WP1_REF.items():
            errs.append(tw_curves(float(w), p)[c] / ref[c] - 1.0)
        worst[c] = max(abs(x) for x in errs)
        print(f"{c:8s}" + "".join(f"{100 * x:+9.2f}%" for x in errs) + f"{100 * worst[c]:11.2f}%")
    lim = ws_limits(p)
    print(f"\nLanding field length limit  W/S = {lim['landing field length']:.1f} N/m2   (WP1: 2206)")
    print(f"Approach speed limit        W/S = {lim['approach speed']:.1f} N/m2")
    # effective climb rate that reproduces the table
    ref = WP1_REF[2200]["climb"]
    lo, hi = 5.0, 30.0
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        if tw_curves(2200.0, md_params(cfg, AR=8.8, CLmax_clean=1.6, climb_rate=mid))["climb"] < ref:
            lo = mid
        else:
            hi = mid
    ceff = 0.5 * (lo + hi)
    print(f"\nCLIMB-RATE CURVE: with c = {cfg['climb_rate']:.3f} m/s (3600 ft/min) the formula gives "
          f"{tw_curves(2200.0, p)['climb']:.4f} at W/S = 2200, the WP1 table has {ref:.4f}.")
    print(f"   The table is reproduced with c = {ceff:.2f} m/s = {ceff / FTMIN2MS:.0f} ft/min.  CHECK THE CLIMB CURVE IN YOUR WP1 DIAGRAM CODE.")
    print("   (It does not change W/S, which is set by the landing field length, only the required T/W.)")
    print("\nCruise, cg119, cg121a, cg121d, tofl and the landing limit reproduce the table (see errors above).")
    print("cg121b and cg121c use a speed rule FITTED to the table: they are approximations (errors above, largest at high W/S).")
    print("They lie far below the binding curves at the design W/S (T/W 0.13-0.17 against 0.22 and more).")
    return worst


# ----------------------------------------------------------------------------------------------
# CLASS I: Breguet fuel fraction
def fuel_fraction(cfg, ws=None, mtom=None):
    if cfg["ld_mode"] == "polar":
        T, pa, rho, a = isa(cfg["h_cr"])
        q = q_cruise(cfg)
        CL = cfg["md_beta_cruise"] * ws / q
        CD = cfg["CD0_clean"] + CL ** 2 / (math.pi * cfg["AR"] * cfg["e_clean"])
        ld = CL / CD
    else:
        ld = cfg["ld_classI"]
    K = cfg["eta_tot"] * ld * cfg["e_fuel"] / G / 1000.0   # km
    x = (cfg["range_design"] + cfg["range_aux"]) / K
    return 1.0 - math.exp(-x), ld


# ----------------------------------------------------------------------------------------------
# GEOMETRY that follows MTOM and W/S
def geometry(cfg, mtom, ws):
    S = mtom * G / ws
    b = math.sqrt(cfg["AR"] * S)
    lam = cfg["taper"]
    cr = 2.0 * S / (b * (1.0 + lam))
    ct = lam * cr
    mac = 2.0 / 3.0 * cr * (1 + lam + lam ** 2) / (1 + lam)
    ymac = b / 6.0 * (1 + 2 * lam) / (1 + lam)
    tanLE = math.tan(math.radians(cfg["sweep_c4"])) + cr / (2.0 * b) * (1.0 - lam)
    sweep_le = math.degrees(math.atan(tanLE))
    L = cfg["L_fus"]
    l_tail = (cfg["x_tail_frac"] - cfg["x_cg_frac"]) * L          # l_H = l_V, WP3.1 3.3
    Sht = cfg["V_H"] * S * mac / l_tail
    Svt = cfg["V_V"] * S * b / l_tail
    return dict(S=S, b=b, cr=cr, ct=ct, mac=mac, ymac=ymac, sweep_le=sweep_le,
                cbar=S / b, Sht=Sht, Svt=Svt, l_tail=l_tail)


# ----------------------------------------------------------------------------------------------
# CLASS II DRAG (report WP3.3 section 4.1):  CD0 = 1/S * sum(Cf*FF*IF*Swet) + CDmisc
def class2_drag(cfg, geo):
    k = cfg["Swet_factor"]
    swet = dict(wing=k * geo["S"], ht=k * geo["Sht"], vt=k * geo["Svt"], fus=cfg["Swet_fus_drag"],
                nac=cfg["Swet_nac"], pyl=cfg["Swet_pyl"])
    area = {c: cfg["Cf_" + c] * cfg["FF_" + c] * cfg["IF_" + c] * swet[c] for c in swet}   # drag area [m2]
    cd0 = sum(area.values()) / geo["S"] + cfg["CD_misc"]
    return cd0, area, swet


def with_drag(cfg, geo):
    """Copy of cfg whose drag polar (CD0 and e of all configurations) follows the current geometry.
    Flap / gear increments of CD0 and of e are the WP1 ones (section 4.1 only covers the clean aircraft)."""
    c = dict(cfg)
    if not cfg["drag_class2"]:
        return c, None
    cd0, area, swet = class2_drag(cfg, geo)
    d = lambda key: INPUTS[key][0] - INPUTS["CD0_clean"][0]
    c["CD0_clean"] = cd0
    for key in ("CD0_TO_ret", "CD0_TO_ext", "CD0_L_ret", "CD0_L_ext"):
        c[key] = cd0 + d(key)
    de = cfg["e_clean"] - INPUTS["e_clean"][0]          # shift of all e if the clean e is overridden
    c["e_TO"] = INPUTS["e_TO"][0] + de
    c["e_L"] = INPUTS["e_L"][0] + de
    return c, dict(cd0=cd0, area=area, swet=swet)


# ----------------------------------------------------------------------------------------------
# LOAD FACTOR: fixed (no V-n diagram)
def compute_nz(cfg, mtom=None, geo=None, oem_for_zfw=None):
    n_max = cfg["n_limit"]
    return dict(n_max=n_max, Nz=cfg["n_safety"] * n_max)


# ----------------------------------------------------------------------------------------------
# RAYMER GA equations 15.46 - 15.59 (lb, ft, ft^2, in, US gal, psf, psi) -> kg
def need(*vals):
    return all(v is not None for v in vals)


def raymer(cfg, mtom, geo, nz, fuel_mass):
    c = {}   # component -> weight [lb] or None
    Wdg = mtom * KG2LB
    Wl = cfg["ldg_mass_frac"] * mtom * KG2LB
    Nz = nz["Nz"]
    q = q_cruise(cfg) * PA2PSF
    Sw = geo["S"] * M22FT2
    Bw = geo["b"] * M2FT
    A, lam = cfg["AR"], cfg["taper"]
    cosL = math.cos(math.radians(cfg["sweep_c4"]))
    NzW = Nz * Wdg
    Wfw = cfg["wing_fuel_frac"] * fuel_mass * KG2LB

    # 15.46 wing
    c["Wing"] = (0.036 * Sw ** 0.758 * Wfw ** 0.0035 * (A / cosL ** 2) ** 0.6 * q ** 0.006 * lam ** 0.04
                 * (100 * cfg["tc_wing"] / cosL) ** -0.3 * NzW ** 0.49)

    reading = cfg["tail_term_reading"]
    if reading not in ("wing", "tail"):
        raise ValueError("tail_term_reading must be 'wing' or 'tail'")

    # 15.47 horizontal tail
    if reading == "wing":
        ok_ht = need(geo["Sht"], cfg["sweep_ht"], cfg["taper_ht"])
    else:
        ok_ht = need(geo["Sht"], cfg["AR_ht"], cfg["sweep_ht"], cfg["taper_ht"], cfg["tc_ht"])
    if ok_ht:
        cl = math.cos(math.radians(cfg["sweep_ht"]))
        if reading == "wing":      # unsubscripted t/c, Lambda and A = wing values (literal reading of the scan)
            tc_term = (100 * cfg["tc_wing"] / cosL) ** -0.12
            ar_term = (A / cl ** 2) ** 0.043
        else:                      # all tail values
            tc_term = (100 * cfg["tc_ht"] / cl) ** -0.12
            ar_term = (cfg["AR_ht"] / cl ** 2) ** 0.043
        c["Horizontal tail"] = (0.016 * NzW ** 0.414 * q ** 0.168 * (geo["Sht"] * M22FT2) ** 0.896
                                * tc_term * ar_term * cfg["taper_ht"] ** -0.02)
    else:
        c["Horizontal tail"] = None

    # 15.48 vertical tail   (Ht/Hv = 1 for a T-tail, 0 for a conventional tail)
    if reading == "wing":
        ok_vt = need(geo["Svt"], cfg["sweep_vt"], cfg["taper_vt"])
    else:
        ok_vt = need(geo["Svt"], cfg["AR_vt"], cfg["sweep_vt"], cfg["taper_vt"], cfg["tc_vt"])
    if ok_vt:
        cl = math.cos(math.radians(cfg["sweep_vt"]))
        HtHv = 1.0 if cfg["T_tail"] else 0.0
        if reading == "wing":
            tc_term = (100 * cfg["tc_wing"] / cl) ** -0.49
            ar_term = (A / cl ** 2) ** 0.357
        else:
            tc_term = (100 * cfg["tc_vt"] / cl) ** -0.49
            ar_term = (cfg["AR_vt"] / cl ** 2) ** 0.357
        c["Vertical tail"] = (0.073 * (1 + 0.2 * HtHv) * NzW ** 0.376 * q ** 0.122 * (geo["Svt"] * M22FT2) ** 0.873
                              * tc_term * ar_term * max(cfg["taper_vt"], 0.2) ** 0.039)
    else:
        c["Vertical tail"] = None

    # 15.49 fuselage (+ pressurisation term, ADDITIVE: 11.9 + (Vpr*Pdelta)^0.271, Raymer p. 407)
    Lf = cfg["L_fus"] * M2FT
    LD = cfg["L_fus"] / cfg["d_fus_outer"]
    Pdelta = (cfg["p_cabin"] - cfg["p_ambient"]) * KPA2PSI
    if need(geo["l_tail"], cfg["V_pressurized"]):
        Vpr = cfg["V_pressurized"] * M32FT3
        Wpress = 11.9 + (Vpr * Pdelta) ** 0.271
        c["Fuselage"] = (0.052 * (cfg["S_wet_fus"] * M22FT2) ** 1.086 * NzW ** 0.177 * (geo["l_tail"] * M2FT) ** -0.051
                         * LD ** -0.072 * q ** 0.241 + Wpress)
    else:
        c["Fuselage"] = None

    # 15.50 / 15.51 landing gear
    if need(cfg["N_gear"], cfg["L_main"]):
        Nl = 1.5 * cfg["N_gear"]
        c["Main gear"] = 0.095 * (Nl * Wl) ** 0.768 * (cfg["L_main"] * M2IN / 12.0) ** 0.409
    else:
        c["Main gear"] = None
    if need(cfg["N_gear"], cfg["L_nose"]):
        Nl = 1.5 * cfg["N_gear"]
        c["Nose gear"] = 0.125 * (Nl * Wl) ** 0.566 * (cfg["L_nose"] * M2IN / 12.0) ** 0.845
    else:
        c["Nose gear"] = None

    # 15.52 installed engines (total)
    Nen = cfg["N_eng"]
    c["Installed engines"] = 2.575 * (cfg["m_engine"] * KG2LB) ** 0.922 * Nen

    # 15.53 fuel system
    Vt_m3 = cfg["fuel_volume"] * (fuel_mass / cfg["fuel_mass_0"] if cfg["scale_fuel_volume"] else 1.0)
    Vt = Vt_m3 * M32GAL
    Vi = cfg["wing_fuel_frac"] * Vt       # integral tank volume
    if cfg["N_tanks"] is not None:
        c["Fuel system"] = 2.49 * Vt ** 0.726 * (1 / (1 + Vi / Vt)) ** 0.363 * cfg["N_tanks"] ** 0.242 * Nen ** 0.157
    else:
        c["Fuel system"] = None

    # 15.54 flight controls
    c["Flight controls"] = 0.053 * Lf ** 1.536 * Bw ** 0.371 * (NzW * 1e-4) ** 0.80

    # 15.55 hydraulics
    c["Hydraulics"] = 0.001 * Wdg

    # 15.57 avionics (installed)
    if cfg["m_avionics_uninstalled"] is not None:
        Wav = 2.117 * (cfg["m_avionics_uninstalled"] * KG2LB) ** 0.933
        c["Avionics"] = Wav
    else:
        Wav = None
        c["Avionics"] = None

    # 15.56 electrical
    if need(c["Fuel system"], Wav):
        c["Electrical"] = 12.57 * (c["Fuel system"] + Wav) ** 0.51
    else:
        c["Electrical"] = None

    # 15.58 air conditioning / anti-ice
    if Wav is not None:
        c["Air-cond. / anti-ice"] = 0.265 * Wdg ** 0.52 * cfg["N_occupants"] ** 0.68 * Wav ** 0.17 * cfg["M_cr"] ** 0.08
    else:
        c["Air-cond. / anti-ice"] = None

    # 15.59 furnishings
    c["Furnishings"] = 0.0582 * Wdg - 65.0

    return {k: (None if v is None else v * cfg["fudge"] / KG2LB) for k, v in c.items()}


# ----------------------------------------------------------------------------------------------
# WING FUEL VOLUME CHECK (WP2 section 5.2.2, Torenbeek)
def wing_fuel_check(cfg, geo, fuel_mass):
    lam = cfg["taper"]
    avail = 0.54 * geo["S"] ** 1.5 / math.sqrt(cfg["AR"]) * cfg["tc_wing"] * (1 + lam + lam ** 2) / (1 + lam) ** 2
    req_wp2 = cfg["fuel_volume"] * (fuel_mass / cfg["fuel_mass_0"])
    req_mass = fuel_mass * cfg["tank_margin"] / cfg["fuel_density"]
    return avail, req_wp2, req_mass


def roll_check(cfg, geo):
    """WP2 section 5.2.5 roll-rate check on the new span. Aileron stations keep the WP2 span fractions."""
    S, b, cr, lam = geo["S"], geo["b"], geo["cr"], cfg["taper"]
    cla, cd0, tau, da, V = 5.979, 0.0065, 0.41, 0.291, 70.0
    b1, b2 = 3.9488 / 9.105 * b / 2.0, 8.1945 / 9.105 * b / 2.0      # same fractions of the semi-span as WP2
    k = cr * (1 - lam) / (b / 2.0)                                      # c(y) = cr - k y
    I = lambda lo, hi, n: sum((cr - k * (lo + (hi - lo) * (i + .5) / 4000)) * (lo + (hi - lo) * (i + .5) / 4000) ** n
                              for i in range(4000)) * (hi - lo) / 4000
    Cld = 2 * cla * tau / (S * b) * I(b1, b2, 1)
    Clp = -4 * (cla + cd0) / (S * b * b) * I(0.0, b / 2.0, 2)
    P = -Cld / Clp * da * 2 * V / b
    return Cld, Clp, P, math.radians(30.0) / P


def pressurised_volume(cfg):
    area = math.pi / 4.0 * cfg["d_fus_inner"] ** 2
    return area * (cfg["l_cabin"] + cfg["l_cargo"] + 0.5 * cfg["l_nose_cone"])


# ----------------------------------------------------------------------------------------------
def build_cfg(strict=False, override=None):
    cfg = {k: v[0] for k, v in INPUTS.items()}
    used = []
    for k, v in TENTATIVE.items():
        cfg[k] = None
        if not strict and v[0] is not None:
            cfg[k] = v[0]
            used.append(k)
    if not strict:
        cfg["V_pressurized"] = pressurised_volume(cfg)
        used.append("V_pressurized")
    if override:
        cfg.update(override)
    return cfg, used


def one_pass(cfg, mtom, ws, oem_guess):
    geo = geometry(cfg, mtom, ws)
    zf, ld = fuel_fraction(cfg, ws, mtom)
    fuel_mass = zf * mtom
    nz = compute_nz(cfg, mtom, geo, oem_guess)
    comp = raymer(cfg, mtom, geo, nz, fuel_mass)
    complete = all(v is not None for v in comp.values())
    empty = sum(v for v in comp.values() if v is not None)
    oem = empty + (cfg["ops_items_frac"] + cfg["trapped_frac"]) * mtom
    mtom_new = (oem + cfg["payload"]) / (1.0 - zf)
    return dict(geo=geo, zf=zf, ld=ld, fuel_mass=fuel_mass, nz=nz, comp=comp, complete=complete,
                empty=empty, oem=oem, mtom_new=mtom_new)


def fmt(x, w=9, d=1):
    return " " * (w - 7) + "missing" if x is None else f"{x:{w}.{d}f}"


def run(strict=False, override=None, verbose=True):
    cfg, used = build_cfg(strict, override)
    tail_missing = []
    if verbose:
        print("=" * 100)
        print("AE2111-I  WP3.4  ITERATION TO A CONVERGED DESIGN   " + ("[STRICT: no assumed values]" if strict else ("[CLASS II DRAG, Breguet L/D from the polar]" if (cfg["drag_class2"] and cfg["ld_mode"] == "polar") else "[WP1 DRAG POLAR, L/D 14]")))
        print(f"Tail-equation symbols (A, t/c, Lambda in Raymer 15.47/15.48) read as: {cfg['tail_term_reading'].upper()} values")
        print(f"Uninstalled avionics mass = {cfg['m_avionics_uninstalled']:.1f} kg = {cfg['m_avionics_uninstalled'] * KG2LB:.0f} lb"
              f"   (Raymer typical {AVIONICS_RANGE_KG[0]:.0f}-{AVIONICS_RANGE_KG[1]:.0f} kg)")
        print("=" * 100)
        if used:
            print("ASSUMED values in use (tail planform and gear, not designed in WP3; NOT results):")
            for k in used:
                src = TENTATIVE[k][2] if k in TENTATIVE else ""
                val = cfg[k]
                print(f"   {k:16s} = {val if not isinstance(val, float) else round(val, 4)}   {src}")
            print()
        ass = [k for k, v in INPUTS.items() if "[ASSUMED]" in v[2]]
        if ass:
            print("ASSUMED drag inputs carried over from WP1 (not given by the Class II drag section):")
            print("   " + ", ".join(f"{k}={cfg[k]}" for k in ass))
            print()

    # missing inputs in strict mode
    miss = [k for k, v in cfg.items() if v is None and not (cfg["tail_term_reading"] == "wing" and k in ("AR_ht", "tc_ht", "AR_vt", "tc_vt"))]
    if miss:
        print("MISSING INPUTS:")
        for k in miss:
            print(f"   {k:16s} {TENTATIVE.get(k, ('', '', ''))[2]}")
        print()

    mtom, ws = cfg["mtom_0"], cfg["ws_0"]
    oem_guess = cfg["oem_classI"]
    hist = []
    for it in range(1, int(cfg["max_iter"]) + 1):
        ws_new = design_point(cfg)["ws"]                   # W/S is set by the landing limits, independent of the drag
        cfg_i, _ = with_drag(cfg, geometry(cfg, mtom, ws_new))
        dp = design_point(cfg_i)
        r = one_pass(cfg_i, mtom, ws_new, oem_guess)
        if not r["complete"]:
            break
        d_mtom = r["mtom_new"] / mtom - 1.0
        d_oem = r["oem"] / oem_guess - 1.0
        d_ws = ws_new / ws - 1.0
        hist.append(dict(it=it, mtom_in=mtom, ws=ws_new, empty=r["empty"], oem=r["oem"], mtom_out=r["mtom_new"],
                         d_mtom=d_mtom, d_oem=d_oem, d_ws=d_ws, nmax=r["nz"]["n_max"], Nz=r["nz"]["Nz"],
                         zf=r["zf"], ld=r["ld"], tw=dp["tw"], cd0=cfg_i["CD0_clean"]))
        converged = it > 1 and max(abs(d_mtom), abs(d_oem), abs(d_ws)) < cfg["tol"]
        mtom, ws, oem_guess = r["mtom_new"], ws_new, r["oem"]
        if converged:
            break

    if not hist:
        print("ITERATION NOT RUN: some Class II components cannot be computed (see missing inputs above).")
        return None
    conv = max(abs(hist[-1]["d_mtom"]), abs(hist[-1]["d_oem"]), abs(hist[-1]["d_ws"])) < cfg["tol"] and len(hist) > 1

    # final state evaluated at the converged MTOM
    ws_fin = design_point(cfg)["ws"]
    cfg, drag = with_drag(cfg, geometry(cfg, mtom, ws_fin))      # from here on cfg holds the converged polar
    dp = design_point(cfg)
    fin = one_pass(cfg, mtom, ws_fin, oem_guess)
    geo = fin["geo"]
    nz = fin["nz"]
    comp = fin["comp"]

    if verbose:
        print("ITERATION HISTORY   (W/S from the matching diagram, MTOM from Class II OEM and the Breguet fuel fraction)")
        print(f"{'it':>3s}{'MTOM in':>10s}{'W/S':>8s}{'Empty':>9s}{'OEM':>9s}{'MTOM out':>10s}{'dMTOM':>9s}{'dOEM':>9s}{'dW/S':>8s}"
              f"{'n_max':>7s}{'Nz':>7s}{'zeta_f':>8s}{'L/D':>6s}{'CD0':>8s}")
        for h in hist:
            print(f"{h['it']:3d}{h['mtom_in']:10.1f}{h['ws']:8.0f}{h['empty']:9.1f}{h['oem']:9.1f}{h['mtom_out']:10.1f}"
                  f"{100 * h['d_mtom']:8.3f}%{100 * h['d_oem']:8.3f}%{100 * h['d_ws']:7.2f}%{h['nmax']:7.3f}{h['Nz']:7.3f}"
                  f"{h['zf']:8.4f}{h['ld']:6.1f}{h['cd0']:8.5f}")
        print(f"\nConverged (all relative changes < {100 * cfg['tol']:.2f} %): {conv}   after {len(hist)} iterations")

        print("\nMATCHING DIAGRAM AT THE CONVERGED DESIGN")
        print(f"   W/S limit by {dp['ws_limit_by']}: {dp['ws_max']:.1f} N/m2  ->  design W/S = {dp['ws']:.0f} N/m2 (rounded down to {cfg['ws_round']:.0f})")
        for k, v in sorted(dp["curves"].items(), key=lambda kv: -kv[1]):
            print(f"   {k:8s} T/W = {v:.4f}" + ("   <- binding" if k == dp["tw_crit"] else ""))
        print(f"   required T/W = {dp['tw_min']:.4f} (+ margin {cfg['tw_margin']:.3f}) = {dp['tw']:.4f}")
        if dp["tw_crit"] == "climb":
            print(f"   NOTE: the climb-rate curve is binding with c = {cfg['climb_rate']:.2f} m/s (3600 ft/min). The WP1 reference table "
                  "is reproduced with about 2835 ft/min (run --validate). W/S is not affected; only the required T/W.")
        T_req = dp["tw"] * fin["mtom_new"] * G / 1000.0
        T_eng = cfg["N_eng"] * cfg["T_engine"]
        print(f"   required thrust = {T_req:.2f} kN   |   installed ({cfg['N_eng']} x FJ44-4A) = {T_eng:.2f} kN   "
              f"-> T/W installed = {T_eng * 1000 / (fin['mtom_new'] * G):.3f}  ({'OK' if T_eng >= T_req else 'NOT ENOUGH'})")

        if drag:
            print("\nCLASS II DRAG at the converged design (section 4.1 method; wing/tail wetted areas follow the geometry)")
            print(f"{'Component':12s}{'Swet [m2]':>11s}{'Cf*FF*IF*Swet [m2]':>22s}{'dCD0':>10s}")
            for k, nm in (("wing", "Wing"), ("ht", "Horizontal tail"), ("vt", "Vertical tail"), ("fus", "Fuselage"),
                          ("nac", "Nacelles"), ("pyl", "Pylons")):
                print(f"{nm:16s}{drag['swet'][k]:7.2f}{drag['area'][k]:22.4f}{drag['area'][k] / geo['S']:10.5f}")
            print(f"{'Misc (wave)':16s}{'':7s}{'':22s}{cfg['CD_misc']:10.5f}")
            print(f"CD0 = {drag['cd0']:.5f}   (WP1 statistical value {INPUTS['CD0_clean'][0]:.5f}, {100 * (drag['cd0'] / INPUTS['CD0_clean'][0] - 1):+.0f} %)")
            CLc = cfg["md_beta_cruise"] * dp["ws"] / q_cruise(cfg)
            CDc = drag["cd0"] + CLc ** 2 / (math.pi * cfg["AR"] * cfg["e_clean"])
            print(f"cruise: CL = {CLc:.3f}, e = {cfg['e_clean']:.4f}, CD = {CDc:.5f}, L/D = {CLc / CDc:.2f}   (Class I used 14.0)")
            print(f"flap/gear polars used by the matching diagram: CD0 TO {cfg['CD0_TO_ret']:.4f}/{cfg['CD0_TO_ext']:.4f}, "
                  f"L {cfg['CD0_L_ret']:.4f}/{cfg['CD0_L_ext']:.4f}; e clean/TO/L = {cfg['e_clean']:.3f}/{cfg['e_TO']:.3f}/{cfg['e_L']:.3f}")
        print(f"\nLOAD FACTOR (fixed): limit n = {nz['n_max']:.2f} (CS 25.337(b) minimum), safety factor {cfg['n_safety']:.2f}, ultimate Nz = {nz['Nz']:.3f}")

        print(f"\nCLASS II COMPONENT MASSES at the converged MTOM")
        print(f"{'Component':26s}{'Weight [kg]':>14s}{'% of MTOM':>12s}")
        print("-" * 52)
        for k, v in comp.items():
            print(f"{k:26s}{fmt(v, 14, 1)}{'' if v is None else f'{100 * v / mtom:11.2f}%'}")
        print("-" * 52)
        print(f"{'Raymer empty weight':26s}{fin['empty']:14.1f}")
        print(f"{'OEM used (empty + ops)':26s}{fin['oem']:14.1f}   (Class I OEM = {cfg['oem_classI']:.1f}, {100 * (fin['oem'] / cfg['oem_classI'] - 1):+.1f} %)")
        print("(Class I OEM contains crew and operational items; the Raymer empty weight does not. Not like for like.)")

        avail, req_wp2, req_mass = wing_fuel_check(cfg, geo, fin["fuel_mass"])
        print(f"\nWING FUEL VOLUME: available (Torenbeek, WP2 5.7) = {avail:.2f} m3 | required: WP2 value scaled with fuel mass = "
              f"{req_wp2:.2f} m3, from this fuel mass ({fin['fuel_mass']:.0f} kg, {cfg['fuel_density']:.0f} kg/m3, x{cfg['tank_margin']}) = {req_mass:.2f} m3"
              f"  -> {'OK' if avail >= max(req_wp2, req_mass) else 'NOT ENOUGH'}")

        Cld, Clp, P, tr = roll_check(cfg, geo)
        print(f"ROLL RATE (WP2 5.2.5 method, aileron stations at the WP2 span fractions): Cl_da = {Cld:.4f}, Cl_p = {Clp:.4f}, "
              f"P = {P:.3f} rad/s -> 30 deg in {tr:.2f} s ({'OK' if tr < 3.0 else 'NOT OK'}, requirement 3 s)")
        print("FLAPS: the flap area ratio Swf/S and hence Delta CLmax (WP2 4.15) are unchanged because AR, taper, sweep and the "
              "flap span fractions are held; the flap area grows with S (WP2: 16.79 m2 at S = 38.62 m2 -> "
              f"{16.79 * geo['S'] / 38.62:.2f} m2).")

        # parameter table: before / after
        mt0, ws0 = cfg["mtom_0"], cfg["ws_0"]
        g0 = geometry(cfg, mt0, ws0)
        g1 = geo
        print("\nPARAMETER TABLE   (before the iteration = WP1/WP2 values, after = converged)")
        print(f"{'Parameter':34s}{'Before':>12s}{'After':>12s}{'Change':>10s}")
        rows = [
            ("MTOM [kg]", mt0, fin["mtom_new"], 1), ("OEM [kg]", cfg["oem_classI"], fin["oem"], 1),
            ("Fuel mass [kg]", cfg["fuel_mass_0"], fin["fuel_mass"], 1), ("Fuel fraction [-]", cfg["fuel_mass_0"] / mt0, fin["zf"], 4),
            ("Wing loading W/S [N/m2]", ws0, dp["ws"], 0), ("T/W required [-]", cfg["tw_0"], dp["tw"], 3),
            ("Wing area S [m2]", g0["S"], g1["S"], 2), ("Wing span b [m]", g0["b"], g1["b"], 2),
            ("Root chord [m]", g0["cr"], g1["cr"], 3), ("Tip chord [m]", g0["ct"], g1["ct"], 3),
            ("MAC [m]", g0["mac"], g1["mac"], 3), ("y_MAC [m]", g0["ymac"], g1["ymac"], 2),
            ("LE sweep [deg]", g0["sweep_le"], g1["sweep_le"], 2),
            ("Horizontal tail area [m2]", g0["Sht"], g1["Sht"], 2), ("Vertical tail area [m2]", g0["Svt"], g1["Svt"], 2),
            ("Tail arm l_H = l_V [m]", g0["l_tail"], g1["l_tail"], 3), ("Nz [-]", None, nz["Nz"], 3),
        ]
        for name, a, b, d in rows:
            ch = "" if a is None or a == 0 else f"{100 * (b / a - 1):+.2f}%"
            print(f"{name:34s}{'' if a is None else f'{a:12.{d}f}'.rjust(12)}{b:12.{d}f}{ch:>10s}")
        print("\nNOT updated in this loop (held at the WP2 value): AR, taper, quarter-chord sweep, t/c, fuselage, engine.")
        if cfg["ld_mode"] == "classI":
            print("L/D for the fuel fraction is the Class I value 14 (--ld=classI).")
    return dict(hist=hist, converged=conv, cfg=cfg, dp=dp, fin=fin, mtom=mtom)


def main():
    argv = sys.argv[1:]
    cfg0, _ = build_cfg()
    if "--validate" in argv:
        validate_matching(cfg0)
        return
    override = {}
    strict = "--strict" in argv
    for a in argv:
        if a.startswith("--av="):
            override["m_avionics_uninstalled"] = float(a.split("=")[1])
        elif a.startswith("--ld="):
            v = a.split("=")[1]
            if v == "classI":
                override["ld_mode"] = "classI"
                override["drag_class2"] = False
            elif v == "polar":
                override["ld_mode"] = "polar"
        elif a.startswith("--e="):
            override["e_clean"] = float(a.split("=")[1])
        elif a.startswith("--ops="):
            override["ops_items_frac"] = float(a.split("=")[1])
        elif a.startswith("--tail=") and a.split("=")[1] in ("wing", "tail"):
            override["tail_term_reading"] = a.split("=")[1]
    tails = [a.split("=")[1] for a in argv if a.startswith("--tail=")]
    readings = ["wing", "tail"] if tails and tails[0] == "both" else [None]
    for rd in readings:
        ov = dict(override)
        if rd:
            ov["tail_term_reading"] = rd
        run(strict, ov)


if __name__ == "__main__":
    main()