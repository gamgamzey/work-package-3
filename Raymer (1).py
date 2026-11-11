import math
import sys

# ----------------------------------------------------------------------------------------------
# unit conversions
KG2LB = 2.20462262
M2FT = 3.280839895
M22FT2 = 10.7639104
M32GAL = 264.172052
PA2PSF = 0.0208854342
KPA2PSI = 0.145037738
M2IN = 39.3700787
G = 9.81
RHO0 = 1.225
A0 = 340.294
P0 = 101325.0

# ----------------------------------------------------------------------------------------------
# INPUTS.  value / unit / source-or-status.   None = PLACEHOLDER (fill in, or use --demo)
# ----------------------------------------------------------------------------------------------
INPUTS = {
    # ---- top level / previous work packages (known) ----
    "mtom_0":        (8660.965,  "kg",   "WP1 final MTOM (starting guess for the iteration)"),
    "oem_classI":    (5283.19,   "kg",   "Class I OEM, for comparison"),
    "payload":       (1010.0,    "kg",   "Top-level requirement"),
    "fuel_mass_0":   (2367.78,   "kg",   "REQ-PROP-11 (= 0.2734 x MTOM). Fuel fraction is derived from this"),
    "ws":            (2200.0,    "N/m2", "WP1 design point, held fixed during the iteration"),
    "ldg_mass_frac": (0.88,      "-",    "Landing mass / MTOM (given)"),
    "M_cr":          (0.68,      "-",    "Top-level requirement"),
    "h_cr":          (12496.8,   "m",    "41,000 ft"),
    # ---- wing (WP2) ----
    "AR":            (8.59,      "-",    "WP2.4"),
    "taper":         (0.363,     "-",    "WP2 (note: reader Eq 2.3 gave 0.400, unresolved)"),
    "sweep_c4":      (10.564,    "deg",  "WP2 quarter-chord sweep"),
    "tc_wing":       (0.14,      "-",    "SC(2)-0414"),
    "wing_fuel_frac": (1.0,      "-",    "ASSUMED: all fuel in wing. Effect on Eq 15.46 is tiny (exponent 0.0035)"),
    "fuel_volume":   (4.115,     "m3",   "WP2.2 required wing fuel volume"),
    "fuel_density":  (800.0,     "kg/m3", "Jet A-1"),
    "scale_fuel_volume": (True,  "-",    "scale tank volume with fuel mass during iteration"),
    # ---- fuselage (WP3.1 report) ----
    "L_fus":         (15.51,     "m",    "Report 3.1.4 (NOTE: drag section uses 27.3 m - inconsistent). Raymer L = structural length, excl. radome and tail cap"),
    "d_fus_inner":   (2.358,     "m",    "Report 3.1.3"),
    "d_fus_outer":   (2.438,     "m",    "Report 3.1.3 (inner + 2 x 40 mm)"),
    "S_wet_fus":     (94.65,     "m2",   "Report 3.1.4"),
    "p_cabin":       (81.2,      "kPa",  "REQ-FUSE-01"),
    "p_ambient":     (17.87,     "kPa",  "REQ-FUSE-01"),
    "tail_arm_Lt":   (6.5142,    "m",    "Tail AC 0.9 L_fus = 13.959 m minus x_CG = 7.4448 m (0.48 L_fus, team decision) = 6.5142 m. Use of x_CG = 7.4448 m confirmed by RK"),
    "l_cabin":       (5.40,      "m",    "WP3.1 eq 3.9 (cabin length)"),
    "l_cargo":       (1.66,      "m",    "WP3.1 sec 3.1.3 (cargo hold length)"),
    "l_nosecone":    (4.72,      "m",    "WP3.1 table 3.4 (nose-cone length)"),
    "cockpit_frac":  (0.5,       "-",    "ASSUMED: half of the nose cone is pressurised (cockpit). Not given in WP3.1/WP3.2"),
    "V_pressurized": ("calc",    "m3",   "= pi/4 d_inner^2 (l_cabin + l_cargo + cockpit_frac l_nosecone) -> 41.1 m3. ASSUMED, not stated in WP3.1/3.2"),
    # ---- empennage (WP3.2d, not yet done). Areas given as ratio to wing area so they follow S ----
    "tail_term_reading": ("wing", "-", "Eq 15.47/15.48 symbols A, t/c, Lambda: 'wing' (literal reading of the scan) or 'tail'. CONFIRM WITH TA"),
    "T_tail":        (True,      "-",    "T-tail selected (WP3.2c) -> Ht/Hv = 1"),
    # tail AREAS: tail-volume method of WP3.2 sec 3.3 (eq 3.11, 3.12), recomputed every pass from the new S, MAC, b
    "V_H":           (0.75,      "-",    "WP3.2 sec 3.3 horizontal tail volume coefficient"),
    "V_V":           (0.076,     "-",    "WP3.2 sec 3.3 vertical tail volume coefficient"),
    # tail SHAPE: NOT given in WP3.2 -> ASSUMED (to be replaced when the tail planform is designed)
    "AR_ht":         (4.5,       "-",    "ASSUMED, not in WP3.2 (only used if tail_term_reading = tail)"),
    "sweep_ht":      (20.0,      "deg",  "ASSUMED, not in WP3.2 (quarter chord)"),
    "taper_ht":      (0.45,      "-",    "ASSUMED, not in WP3.2"),
    "tc_ht":         (0.10,      "-",    "ASSUMED, not in WP3.2 (only used if tail_term_reading = tail)"),
    "AR_vt":         (1.2,       "-",    "ASSUMED, not in WP3.2 (T-tail fin: low AR; only used if tail_term_reading = tail)"),
    "sweep_vt":      (35.0,      "deg",  "ASSUMED, not in WP3.2 (quarter chord)"),
    "taper_vt":      (0.8,       "-",    "ASSUMED, not in WP3.2 (WP3.2 sec 3.2.3: T-tail fin taper close to one)"),
    "tc_vt":         (0.10,      "-",    "ASSUMED, not in WP3.2 (only used if tail_term_reading = tail)"),
    # ---- landing gear (WP3.2 landing gear, section 3.4.4 still empty) ----
    "N_gear":        (2.5,       "-",    "WP3.2 REQ-LAND-01a (2.5 g). Nl = 1.5 x N_gear. (REQ-LAND-01b mentions 3 for the ultimate: unclear, see notes)"),
    "L_main":        (1.5,       "m",    "Main gear strut length ~150 cm (RK; WP3.2 eq 3.20 gives 1.4583 m minimum for tail strike)"),
    "L_nose":        (1.5,       "m",    "ASSUMED = main strut length (150 cm, RK)"),
    # ---- propulsion ----
    "N_eng":         (2,         "-",    "Two engines"),
    "m_engine":      (304.0,     "kg",   "FJ44-4A dry mass each (Table 2.3)"),
    # ---- systems ----
    "N_tanks":       (2,      "-",    "2 fuel tanks"),
    "m_avionics_uninstalled": (800.0 / KG2LB, "kg", "800 lb = 362.9 kg uninstalled avionics (low end of Raymer's 800-1400 lb range; to be discussed with TA)"),
    "N_occupants":   (12,        "-",    "10 passengers + 2 pilots (REQ-FUSE-03)"),
    # ---- how Class II is turned into OEM (DECISIONS: slide 27/40 ranges given in comments) ----
    "ops_items_frac": (0.0,      "-",    "0 = pure Raymer (empty weight only). Lecture slides: operational items incl. crew are 5-10 % of MTOM"),
    "trapped_frac":  (0.0,       "-",    "0 = pure Raymer. Lecture slides: trapped fuel + oil 0.1-0.5 % of MTOM"),
    "fudge":         (1.0,       "-",    "Raymer Table 15.4: 1.0 conventional aluminium"),
    # ---- load factor (fixed by team decision, no V-n calculation) ----
    "n_limit":       (2.5,       "-",    "Limit load factor, fixed at 2.5 (team decision, replaces the CS-25 V-n calculation)"),
    "n_safety":      (1.5,       "-",    "Safety factor: ultimate load factor Nz = 1.5 x n_limit = 3.75 (Raymer's Nz is the ULTIMATE value). Set 1.0 if 2.5 is meant as Nz itself"),
    # ---- iteration ----
    "tol":           (0.01,      "-",    "Convergence on OEM change (<1 %, lecture slide)"),
    "max_iter":      (30,        "-",    ""),
}

# DEMO guesses - ONLY used with --demo and only for inputs that are None above. NOT RESULTS.
DEMO = {
    # (no placeholders left: WP3.1 / WP3.2 values are filled in; --demo now changes nothing)
}
AVIONICS_RANGE_KG = (363.0, 635.0)   # Raymer's own guidance for uninstalled avionics (800-1400 lb)


def get(cfg, key):
    return cfg[key]


# ----------------------------------------------------------------------------------------------
# atmosphere
def isa(h):
    if h <= 11000.0:
        T = 288.15 - 0.0065 * h
        p = 101325.0 * (T / 288.15) ** 5.25588
    else:
        T = 216.65
        p = 22632.06 * math.exp(-9.80665 * (h - 11000.0) / (287.058 * 216.65))
    rho = p / (287.058 * T)
    return T, p, rho, math.sqrt(1.4 * 287.058 * T)


def q_cruise(cfg):
    _, p, _, _ = isa(cfg["h_cr"])
    return 0.5 * 1.4 * p * cfg["M_cr"] ** 2  # Pa


# ----------------------------------------------------------------------------------------------
# geometry that follows MTOM (S from fixed W/S, span from fixed AR)
def geometry(cfg, mtom):
    S = mtom * G / cfg["ws"]
    b = math.sqrt(cfg["AR"] * S)
    cr = 2 * S / (b * (1 + cfg["taper"]))
    cbar_geo = S / b                       # mean geometric chord (used by CS-25 gust formula)
    lam = cfg["taper"]
    mac = 2.0 / 3.0 * cr * (1 + lam + lam ** 2) / (1 + lam)
    g = dict(S=S, b=b, cr=cr, cbar=cbar_geo, mac=mac)
    # tail areas by the tail-volume method (WP3.2 eq 3.11, 3.12); the arm l = L_t is fixed by the fuselage
    g["Sht"] = cfg["V_H"] * S * mac / cfg["tail_arm_Lt"]
    g["Svt"] = cfg["V_V"] * S * b / cfg["tail_arm_Lt"]
    return g


# ----------------------------------------------------------------------------------------------
# load factor: fixed, no V-n diagram
def compute_nz(cfg, mtom, geo, oem_for_zfw=None):
    n_max = cfg["n_limit"]
    return dict(n_max=n_max, Nz=cfg["n_safety"] * n_max)


# ----------------------------------------------------------------------------------------------
# Raymer GA equations 15.46 - 15.59 (lb, ft, ft^2, in, US gal, psf, psi) -> lb
def need(*vals):
    return all(v is not None for v in vals)


def raymer(cfg, mtom, geo, nz):
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
    fuel_mass = cfg["fuel_mass_0"] * (mtom / cfg["mtom_0"])    # scales with MTOM (constant fuel fraction)
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
        if reading == "wing":      # unsubscripted t/c and A = wing values; Lambda_vt is the vertical-tail sweep
            tc_term = (100 * cfg["tc_wing"] / cl) ** -0.49
            ar_term = (A / cl ** 2) ** 0.357
        else:
            tc_term = (100 * cfg["tc_vt"] / cl) ** -0.49
            ar_term = (cfg["AR_vt"] / cl ** 2) ** 0.357
        c["Vertical tail"] = (0.073 * (1 + 0.2 * HtHv) * NzW ** 0.376 * q ** 0.122 * (geo["Svt"] * M22FT2) ** 0.873
                              * tc_term * ar_term * cfg["taper_vt"] ** 0.039)
    else:
        c["Vertical tail"] = None

    # 15.49 fuselage (+ pressurisation term, ADDITIVE: 11.9 + (Vpr*Pdelta)^0.271)
    Lf = cfg["L_fus"] * M2FT
    LD = cfg["L_fus"] / cfg["d_fus_outer"]
    Pdelta = (cfg["p_cabin"] - cfg["p_ambient"]) * KPA2PSI
    if need(cfg["tail_arm_Lt"], cfg["V_pressurized"]):
        Vpr = cfg["V_pressurized"] * 35.3146667
        Wpress = 11.9 + (Vpr * Pdelta) ** 0.271
        c["Fuselage"] = (0.052 * (cfg["S_wet_fus"] * M22FT2) ** 1.086 * NzW ** 0.177 * (cfg["tail_arm_Lt"] * M2FT) ** -0.051
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

    # fudge factor and conversion to kg
    return {k: (None if v is None else v * cfg["fudge"] / KG2LB) for k, v in c.items()}


# ----------------------------------------------------------------------------------------------
def build_cfg(demo, override=None):
    cfg = {k: v[0] for k, v in INPUTS.items()}
    if override:
        cfg.update(override)
    if cfg["V_pressurized"] == "calc":     # pressurised volume from the WP3.1 fuselage layout
        cfg["V_pressurized"] = (math.pi / 4 * cfg["d_fus_inner"] ** 2
                                * (cfg["l_cabin"] + cfg["l_cargo"] + cfg["cockpit_frac"] * cfg["l_nosecone"]))
    used = []
    if demo:
        for k, v in DEMO.items():
            if cfg.get(k) is None:
                cfg[k] = v
                used.append(k)
    return cfg, used


def missing_inputs(cfg):
    skip = {"AR_ht", "tc_ht", "AR_vt", "tc_vt"} if cfg["tail_term_reading"] == "wing" else set()
    return [(k, INPUTS[k][1], INPUTS[k][2]) for k, v in cfg.items() if v is None and k not in skip]


def fmt(x, w=9, d=1):
    return " " * (w - 7) + "missing" if x is None else f"{x:{w}.{d}f}"


# ----------------------------------------------------------------------------------------------
# INPUT TABLE of the report (Table: Inputs of the Class II weight estimation), evaluated at the START of the iteration
# (MTOM = mtom_0, Class I geometry). Printed so that it can be compared line by line with the LaTeX table.
def input_table(cfg):
    m0 = cfg["mtom_0"]
    geo = geometry(cfg, m0)
    q = q_cruise(cfg)
    dP = cfg["p_cabin"] - cfg["p_ambient"]
    nz = compute_nz(cfg, m0, geo)
    # (label, value used by the code, value printed in the report table, unit)
    return [
        ("Design gross weight W_dg",          m0,                          8661,   "kg"),
        ("Landing weight W_l",                cfg["ldg_mass_frac"] * m0,   7622,   "kg"),
        ("Ultimate load factor N_z",          nz["Nz"],                    3.75,   "-"),
        ("Wing area S_w",                     geo["S"],                    38.62,  "m2"),
        ("Wing span B_w",                     geo["b"],                    18.21,  "m"),
        ("Aspect ratio A",                    cfg["AR"],                   8.59,   "-"),
        ("Taper ratio lambda",                cfg["taper"],                0.363,  "-"),
        ("Quarter-chord sweep",               cfg["sweep_c4"],             10.56,  "deg"),
        ("Thickness ratio t/c",               cfg["tc_wing"],              0.14,   "-"),
        ("Dynamic pressure q",                q,                           5785,   "Pa"),
        ("Dynamic pressure q",                q * PA2PSF,                  120.8,  "lb/ft2"),
        ("Fuel mass in wing W_fw",            cfg["wing_fuel_frac"] * cfg["fuel_mass_0"], 2368, "kg"),
        ("Fuel mass in wing W_fw",            cfg["wing_fuel_frac"] * cfg["fuel_mass_0"] * KG2LB, 5220, "lb"),
        ("Horizontal tail area S_ht",         geo["Sht"],                  10.11,  "m2"),
        ("HT sweep",                          cfg["sweep_ht"],             20.0,   "deg"),
        ("HT taper ratio",                    cfg["taper_ht"],             0.45,   "-"),
        ("HT aspect ratio",                   cfg["AR_ht"],                4.5,    "-"),
        ("Vertical tail area S_vt",           geo["Svt"],                  8.21,   "m2"),
        ("VT sweep",                          cfg["sweep_vt"],             35.0,   "deg"),
        ("VT taper ratio",                    cfg["taper_vt"],             0.8,    "-"),
        ("VT aspect ratio",                   cfg["AR_vt"],                1.2,    "-"),
        ("Tail position Ht/Hv (T-tail)",      1.0 if cfg["T_tail"] else 0.0, 1,    "-"),
        ("Fuselage wetted area S_f",          cfg["S_wet_fus"],            94.65,  "m2"),
        ("Fuselage length L",                 cfg["L_fus"],                15.51,  "m"),
        ("Fuselage outer diameter D",         cfg["d_fus_outer"],          2.438,  "m"),
        ("Tail arm L_t",                      cfg["tail_arm_Lt"],          6.51,   "m"),
        ("Pressurised volume V_pr",           cfg["V_pressurized"],        41.1,   "m3"),
        ("Pressurised volume V_pr",           cfg["V_pressurized"] * 35.3146667, 1453, "ft3"),
        ("Cabin pressure difference",         dP,                          63.3,   "kPa"),
        ("Cabin pressure difference",         dP * KPA2PSI,                9.2,    "psi"),
        ("Landing gear load factor basis",    cfg["N_gear"],               2.5,    "-"),
        ("Main strut length L_m",             cfg["L_main"],               1.5,    "m"),
        ("Nose strut length L_n",             cfg["L_nose"],               1.5,    "m"),
        ("Engine mass (dry)",                 cfg["m_engine"],             304.0,  "kg"),
        ("Number of engines",                 cfg["N_eng"],                2,      "-"),
        ("Total fuel volume V_t",             cfg["fuel_volume"],          4.115,  "m3"),
        ("Total fuel volume V_t",             cfg["fuel_volume"] * M32GAL, 1087,   "US gal"),
        ("Integral tank volume V_i (= V_t)",  cfg["wing_fuel_frac"] * cfg["fuel_volume"], 4.115, "m3"),
        ("Number of fuel tanks N_t",          cfg["N_tanks"],              2,      "-"),
        ("Uninstalled avionics mass",         cfg["m_avionics_uninstalled"], 363,  "kg"),
        ("Uninstalled avionics mass",         cfg["m_avionics_uninstalled"] * KG2LB, 800, "lb"),
        ("Persons on board N_p",              cfg["N_occupants"],          12,     "-"),
        ("Cruise Mach number",                cfg["M_cr"],                 0.68,   "-"),
        ("Technology factor k",               cfg["fudge"],                1.0,    "-"),
    ]


def print_input_table(cfg):
    print("INPUTS AT THE START OF THE ITERATION (MTOM = Class I value) - compare with the report table 'Inputs of the Class II weight estimation'")
    print(f"{'Parameter':36s}{'Code value':>14s}{'Report table':>14s}  {'Unit':8s}{'Match':>6s}")
    allok = True
    for name, val, tab, unit in input_table(cfg):
        # a table entry is rounded: it matches when rounding the code value to the same number of significant digits agrees
        tol = max(abs(tab) * 6e-3, 6e-3 if abs(tab) < 1 else 0.0) if tab else 1e-9
        ok = abs(val - tab) <= max(tol, 0.5 * 10 ** (-(len(str(tab).split('.')[1]) if '.' in str(tab) else 0)))
        allok &= ok
        print(f"{name:36s}{val:14.4f}{tab:14g}  {unit:8s}{'ok' if ok else 'DIFF':>6s}")
    print("All inputs agree with the report table." if allok else "SOME INPUTS DIFFER FROM THE REPORT TABLE (see DIFF).")
    print()
    return allok


def run(demo=False, override=None):
    cfg, used = build_cfg(demo, override)
    miss = missing_inputs(cfg)
    print("=" * 92)
    print("AE2111 WP3.3b - Class II weight estimation (Raymer GA 15.46-15.59)" + ("   ** DEMO MODE **" if demo else ""))
    print(f"Tail-equation symbols (A, t/c, Lambda in Eq 15.47/15.48) read as: {cfg['tail_term_reading'].upper()} values")
    print("=" * 92)
    if demo and used:
        print("DEMO placeholders in use (NOT real values, results below are NOT valid):")
        for k in used:
            print(f"   {k:26s} = {cfg[k]}   [{INPUTS[k][1]}]")
        print()
    if miss:
        print("MISSING INPUTS (placeholders):")
        for k, u, s in miss:
            print(f"   {k:26s} [{u}]  {s}")
        print()

    print_input_table(cfg)

    # first pass at baseline MTOM, to show what can already be computed
    fuel_frac = cfg["fuel_mass_0"] / cfg["mtom_0"]
    mtom = cfg["mtom_0"]
    oem_guess = cfg["oem_classI"]
    hist = []
    for it in range(1, int(cfg["max_iter"]) + 1):
        geo = geometry(cfg, mtom)
        nz = compute_nz(cfg, mtom, geo, oem_guess)
        comp = raymer(cfg, mtom, geo, nz)
        known = sum(v for v in comp.values() if v is not None)
        complete = all(v is not None for v in comp.values())
        if not complete:
            break
        empty = known
        oem = empty + (cfg["ops_items_frac"] + cfg["trapped_frac"]) * mtom
        mtom_new = (oem + cfg["payload"]) / (1 - fuel_frac)
        d_oem = (oem - oem_guess) / oem_guess
        hist.append((it, mtom, empty, oem, mtom_new, d_oem, nz["n_max"], nz["Nz"], geo["S"], geo["b"]))
        oem_guess = oem
        if abs(d_oem) < cfg["tol"] and it > 1:
            mtom = mtom_new
            break
        mtom = mtom_new

    # report of the last pass
    geo = geometry(cfg, cfg["mtom_0"] if not hist else hist[-1][1])
    mt_show = cfg["mtom_0"] if not hist else hist[-1][1]
    nz = compute_nz(cfg, mt_show, geo, oem_guess)
    comp = raymer(cfg, mt_show, geo, nz)
    print(f"Load factor (fixed): n_limit = {nz['n_max']:.2f}, safety factor {cfg['n_safety']:.2f},  Nz = {nz['Nz']:.3f}")
    print(f"RESULTS OF THE LAST ITERATION (MTOM in = {mt_show:,.1f} kg; the geometry below belongs to THIS mass, not to the Class I inputs above)")
    print(f"Geometry: S = {geo['S']:.2f} m2, b = {geo['b']:.2f} m, c_root = {geo['cr']:.2f} m, S_ht = {geo['Sht']:.2f} m2, S_vt = {geo['Svt']:.2f} m2,  q_cruise = {q_cruise(cfg):.0f} Pa")
    print()
    print(f"{'Component':26s}{'Weight [kg]':>14s}{'% of MTOM':>12s}")
    print("-" * 52)
    tot = 0.0
    for k, v in comp.items():
        if v is not None:
            tot += v
        print(f"{k:26s}{fmt(v, 14, 1)}{'' if v is None else f'{100 * v / mt_show:11.2f}%'}")
    print("-" * 52)
    note = "" if all(v is not None for v in comp.values()) else "   (INCOMPLETE - missing components)"
    print(f"{'Raymer empty weight':26s}{tot:14.1f}{note}")
    print("(Raymer = EMPTY weight only. 'OEM' below = empty + the ops/trapped fractions set in INPUTS (0 = pure Raymer).)")
    print()

    if hist:
        print("ITERATION  (Class II OEM -> MTOM = (OEM + payload)/(1 - fuel fraction), W/S and AR fixed)")
        print(f"fuel fraction = {fuel_frac:.4f}  (= {cfg['fuel_mass_0']} kg / {cfg['mtom_0']} kg)")
        print(f"{'it':>3s}{'MTOM in':>11s}{'S [m2]':>9s}{'b [m]':>8s}{'Empty':>10s}{'OEM':>10s}{'MTOM out':>11s}{'dOEM':>9s}{'n_max':>8s}{'Nz':>7s}")
        for it, mi, em, oe, mo, dd, nm, nzz, S_, b_ in hist:
            print(f"{it:3d}{mi:11.1f}{S_:9.2f}{b_:8.2f}{em:10.1f}{oe:10.1f}{mo:11.1f}{100 * dd:8.2f}%{nm:8.3f}{nzz:7.3f}")
        last = hist[-1]
        conv = abs(last[5]) < cfg["tol"]
        print(f"\nConverged: {conv}   |   Class II OEM = {last[3]:.1f} kg vs Class I OEM = {cfg['oem_classI']:.1f} kg "
              f"({100 * (last[3] / cfg['oem_classI'] - 1):+.1f} %)")
        print(f"New MTOM = {last[4]:.1f} kg (was {cfg['mtom_0']:.1f} kg, {100 * (last[4] / cfg['mtom_0'] - 1):+.1f} %)")
        g2 = geometry(cfg, last[4])
        print(f"New S = {g2['S']:.2f} m2, b = {g2['b']:.2f} m, T = {0.232 * last[4] * G / 1000:.2f} kN (T/W = 0.232 fixed)")
    else:
        print("ITERATION not run: fill in all placeholders (or use --demo to see the chain work).")
    if demo:
        print("\n*** DEMO MODE: every number above that depends on a DEMO placeholder is a dummy. ***")


if __name__ == "__main__":
    demo = "--demo" in sys.argv
    av_args = [a for a in sys.argv if a.startswith("--av=")]
    tail_args = [a for a in sys.argv if a.startswith("--tail=")]
    if tail_args:
        choice = tail_args[0].split("=")[1]
        readings = ["wing", "tail"] if choice == "both" else [choice]
    else:
        readings = [INPUTS["tail_term_reading"][0]]

    if av_args:                                    # python wp33b_raymer_pure.py --av=450
        avs = [float(av_args[0].split("=")[1])]
    elif INPUTS["m_avionics_uninstalled"][0] is not None:
        avs = [None]                               # use the value in INPUTS
    else:                                          # avionics mass not decided: run Raymer's low and high end
        avs = list(AVIONICS_RANGE_KG)

    for reading in readings:
        for av in avs:
            override = {"tail_term_reading": reading}
            if av is not None:
                override["m_avionics_uninstalled"] = av
            if len(readings) > 1 or len(avs) > 1 or av is not None:
                print("\n" + "#" * 92)
                print(f"# TAIL READING = {reading.upper()}" + (f"   |   UNINSTALLED AVIONICS = {av:.0f} kg  (Raymer range "
                      f"{AVIONICS_RANGE_KG[0]:.0f}-{AVIONICS_RANGE_KG[1]:.0f} kg)" if av is not None else ""))
                print("#" * 92)
            run(demo, override)