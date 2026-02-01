import sys
import numpy as np
import pandas as pd
from scipy.stats import spearmanr


# =======================
# DEFAULT CONFIGURATION
# =======================

DEFAULT_INPUT_CSV = r"C:/.csv"
DEFAULT_OUTPUT_CSV = r"C:/.csv"

EPS = 1e-6

GROUP_COLS = ["Name", "index_name", "altitude_m", "Type"]
VALUE_COL = "Mean index value"


# =======================
# COMPUTATION ENGINE
# =======================

def compute_metrics(y):
    y = np.asarray(y, dtype=float)

    # --- BASIC LEVEL STATISTICS ---
    mean_index = np.mean(y)
    sd_index = np.std(y, ddof=1)
    cv_index = sd_index / mean_index if mean_index > 0 else np.nan

    # --- DIFFERENCES ---
    delta = np.diff(y)
    abs_delta = np.abs(delta)

    # absolute amplitudes
    A = abs_delta.sum()
    G = np.clip(delta, 0, None).sum()
    D = np.clip(-delta, 0, None).sum()

    # percentage amplitudes
    pct = delta / (y[:-1] + EPS)
    A_pct = np.abs(pct).sum()
    G_pct = np.clip(pct, 0, None).sum()
    D_pct = np.clip(-pct, 0, None).sum()

    # number of increases/decreases
    n_growth = np.sum(delta > 0)
    n_drop = np.sum(delta < 0)

    # jerkiness (second difference)
    J = np.abs(np.diff(delta)).sum() if len(delta) >= 2 else np.nan

    # concentration of changes
    if A > 0:
        p = abs_delta / A
        C = np.sum(p ** 2)
    else:
        C = np.nan

    # movement relative to margin 0–1 For indicator analysis values ​​that are not in the 0-1 range, the range should be adjusted, also for the current full set for MCARI
    u_plus = np.clip(delta, 0, None) / (1 - y[:-1] + EPS)
    u_minus = np.clip(-delta, 0, None) / (y[:-1] + EPS)
    u = u_plus + u_minus

    A_u = u.sum()
    J_u = np.abs(np.diff(u)).sum() if len(u) >= 2 else np.nan

    # level-motion correlation
    m = (y[:-1] + y[1:]) / 2
    a = abs_delta

    if len(a) >= 3 and np.std(a) > 0 and np.std(m) > 0:
        K, _ = spearmanr(m, a)
    else:
        K = np.nan

    return {
        "Mean_index": mean_index,
        "SD_index": sd_index,
        "CV_index": cv_index,

        "A_total": A,
        "A_growth": G,
        "A_drop": D,

        "A_pct_total": A_pct,
        "A_pct_growth": G_pct,
        "A_pct_drop": D_pct,

        "n_growth": n_growth,
        "n_drop": n_drop,

        "J_roughness": J,
        "C_concentration": C,

        "A_u_margin": A_u,
        "J_u_margin": J_u,
        "K_level_motion": K
    }


# =======================
# PIPELINE
# =======================

def main(input_csv, output_csv):
    print(f"📥 Loading data from: {input_csv}")
    df = pd.read_csv(input_csv)

    results = []

    for keys, g in df.groupby(GROUP_COLS):
        g = g.sort_values("measurement")
        y = g[VALUE_COL].values

        if len(y) < 2 or np.isnan(y).any():
            continue

        metrics = compute_metrics(y)
        row = dict(zip(GROUP_COLS, keys))
        row.update(metrics)
        results.append(row)

    out = pd.DataFrame(results)
    out.to_csv(output_csv, index=False)

    print(f"✅ Save {len(out)} poems to:")
    print(output_csv)


# =======================
# LAUNCH
# =======================

if __name__ == "__main__":

    # if arguments are given → use them
    if len(sys.argv) == 3:
        input_csv = sys.argv[1]
        output_csv = sys.argv[2]

    # if not → use default paths
    else:
        print("⚠️ No paths given - using defaults")
        input_csv = DEFAULT_INPUT_CSV
        output_csv = DEFAULT_OUTPUT_CSV

    main(input_csv, output_csv)
