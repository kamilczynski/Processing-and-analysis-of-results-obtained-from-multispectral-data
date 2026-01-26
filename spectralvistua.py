import sys
import numpy as np
import pandas as pd
from scipy.stats import spearmanr


# =======================
# KONFIGURACJA DOMYŚLNA
# =======================

DEFAULT_INPUT_CSV = r"C:/Users/topgu/Desktop/Art/OSTATNIE ARTYKULY/ZAGESZCZENIE/WYNIKI zageszczenie/jesiennabigmerge.csv"
DEFAULT_OUTPUT_CSV = r"C:/Users/topgu/Desktop/Art/OSTATNIE ARTYKULY/ZAGESZCZENIE/WYNIKI zageszczenie/wyniki_dynamika.csv"

EPS = 1e-6

GROUP_COLS = ["Name", "index_name", "altitude_m", "Type"]
VALUE_COL = "Mean index value"


# =======================
# SILNIK OBLICZENIOWY
# =======================

def compute_metrics(y):
    y = np.asarray(y, dtype=float)

    # --- PODSTAWOWE STATYSTYKI POZIOMU ---
    mean_index = np.mean(y)
    sd_index = np.std(y, ddof=1)
    cv_index = sd_index / mean_index if mean_index > 0 else np.nan

    # --- RÓŻNICE ---
    delta = np.diff(y)
    abs_delta = np.abs(delta)

    # amplitudy absolutne
    A = abs_delta.sum()
    G = np.clip(delta, 0, None).sum()
    D = np.clip(-delta, 0, None).sum()

    # amplitudy procentowe
    pct = delta / (y[:-1] + EPS)
    A_pct = np.abs(pct).sum()
    G_pct = np.clip(pct, 0, None).sum()
    D_pct = np.clip(-pct, 0, None).sum()

    # liczba wzrostów / spadków
    n_growth = np.sum(delta > 0)
    n_drop = np.sum(delta < 0)

    # szarpaność (druga różnica)
    J = np.abs(np.diff(delta)).sum() if len(delta) >= 2 else np.nan

    # koncentracja zmian
    if A > 0:
        p = abs_delta / A
        C = np.sum(p ** 2)
    else:
        C = np.nan

    # ruch względem marginesu 0–1
    u_plus = np.clip(delta, 0, None) / (1 - y[:-1] + EPS)
    u_minus = np.clip(-delta, 0, None) / (y[:-1] + EPS)
    u = u_plus + u_minus

    A_u = u.sum()
    J_u = np.abs(np.diff(u)).sum() if len(u) >= 2 else np.nan

    # korelacja poziom–ruch
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
    print(f"📥 Wczytuję dane z: {input_csv}")
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

    print(f"✅ Zapisano {len(out)} wierszy do:")
    print(output_csv)


# =======================
# URUCHOMIENIE
# =======================

if __name__ == "__main__":

    # jeśli podano argumenty → użyj ich
    if len(sys.argv) == 3:
        input_csv = sys.argv[1]
        output_csv = sys.argv[2]

    # jeśli nie → użyj domyślnych ścieżek
    else:
        print("⚠️ Nie podano ścieżek — używam domyślnych")
        input_csv = DEFAULT_INPUT_CSV
        output_csv = DEFAULT_OUTPUT_CSV

    main(input_csv, output_csv)
