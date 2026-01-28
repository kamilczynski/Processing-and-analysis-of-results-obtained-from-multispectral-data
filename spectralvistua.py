import sys
import numpy as np
import pandas as pd
from scipy.stats import spearmanr

# =======================
# KONFIGURACJA DOMYŚLNA
# =======================

DEFAULT_INPUT_CSV = r"C:/Users/topgu/Desktop/Art/OSTATNIE ARTYKULY/ZAGESZCZENIE/WYNIKI zageszczenie/jesiennabigmerge.csv"
DEFAULT_OUTPUT_CSV = r"C:/Users/topgu/Desktop/Art/OSTATNIE ARTYKULY/ZAGESZCZENIE/WYNIKI zageszczenie/wyniki_dynamikapoprawione.csv"

EPS = 1e-6

GROUP_COLS = ["Name", "index_name", "altitude_m", "Type"]
# =======================
# CUSTOM NAME LABELS
# =======================

NAME_LABELS = {
    "ENRO2malykwadrat": "Enrosadira 2 Bounded",
    "ENRO3malykwadrat": "Enrosadira 3 Bounded",
    "ENRO4malykwadrat": "Enrosadira 4 Bounded",
    "ENRO5malykwadrat": "Enrosadira 5 Bounded",

    "POLO2malykwadrat": "Polonez 2 Bounded",
    "POLO3malykwadrat": "Polonez 3 Bounded",
    "POLO4malykwadrat": "Polonez 4 Bounded",
    "POLO5malykwadrat": "Polonez 5 Bounded",

    "ENRO2duzykwadrat": "Enrosadira 2 Edges",
    "ENRO3duzykwadrat": "Enrosadira 3 Edges",
    "ENRO4duzykwadrat": "Enrosadira 4 Edges",
    "ENRO5duzykwadrat": "Enrosadira 5 Edges",

    "POLO2duzykwadrat": "Polonez 2 Edges",
    "POLO3duzykwadrat": "Polonez 3 Edges",
    "POLO4duzykwadrat": "Polonez 4 Edges",
    "POLO5duzykwadrat": "Polonez 5 Edges",
}

VALUE_COL_MEAN = "Mean index value"
VALUE_COL_SD = "Index value SD"


# =======================
# SILNIK OBLICZENIOWY
# =======================

def compute_metrics(y_mean, y_sd):
    y_mean = np.asarray(y_mean, dtype=float)
    y_sd = np.asarray(y_sd, dtype=float)

    # =======================
    # POZIOM (CZAS)
    # =======================

    mean_index = np.mean(y_mean)


    # =======================
    # CV PRZESTRZENNE (PO TERMINACH)
    # =======================

    cv_spatial_i = y_sd / (y_mean + EPS)
    cv_spatial_mean = np.mean(cv_spatial_i)


    # =======================
    # ZMIENNOŚĆ PRZESTRZENNA (SD)
    # =======================

    mean_index_sd = np.mean(y_sd)
    sd_index_sd = np.std(y_sd, ddof=1)

    # =======================
    # RÓŻNICE CZASOWE
    # Δ_i = y_i − y_{i+1}
    # =======================

    delta = -np.diff(y_mean)
    abs_delta = np.abs(delta)

    A_pos = delta[delta > 0].sum()          # wzrosty
    A_neg = (-delta[delta < 0]).sum()       # spadki (moduł)
    A_total = A_pos + A_neg

    # =======================
    # RÓŻNICE PROCENTOWE
    # =======================

    pct = delta / (y_mean[:-1] + EPS)

    A_pct_pos = pct[pct > 0].sum()
    A_pct_neg = (-pct[pct < 0]).sum()
    A_pct_total = A_pct_pos + A_pct_neg

    # =======================
    # CZĘSTOŚĆ ZMIAN
    # =======================

    n_pos = np.sum(delta > 0)
    n_neg = np.sum(delta < 0)

    # =======================
    # SZARPNOŚĆ
    # =======================

    J = np.abs(np.diff(delta)).sum() if len(delta) >= 2 else np.nan

    # =======================
    # KONCENTRACJA ZMIAN
    # =======================

    if A_total > 0:
        p = abs_delta / A_total
        C = np.sum(p ** 2)
    else:
        C = np.nan

    # =======================
    # NORMALIZACJA DO MARGINESU 0–1
    # =======================

    u = np.zeros_like(delta, dtype=float)

    mask_pos = delta > 0
    mask_neg = delta < 0

    u[mask_pos] = delta[mask_pos] / (1 - y_mean[:-1][mask_pos] + EPS)
    u[mask_neg] = (-delta[mask_neg]) / (y_mean[:-1][mask_neg] + EPS)

    A_u = u.sum()
    J_u = np.abs(np.diff(u)).sum() if len(u) >= 2 else np.nan

    # =======================
    # POZIOM vs RUCH (SPEARMAN)
    # =======================

    m = (y_mean[:-1] + y_mean[1:]) / 2
    a = abs_delta

    if len(a) >= 3 and np.std(a) > 0 and np.std(m) > 0:
        K, _ = spearmanr(m, a)
    else:
        K = np.nan

    # =======================
    # SANITY CHECK
    # =======================

    if not np.isclose(A_pos + A_neg, A_total):
        raise RuntimeError("BŁĄD LOGIKI: A_pos + A_neg != A_total")

    # =======================
    # ZWROT WYNIKÓW
    # =======================

    return {
        # poziom czasowy
        "Mean vegetation index value": mean_index,


        # CV przestrzenne
        "Mean coefficient of variation of vegetation index": cv_spatial_mean,


        # SD przestrzenne
        "Mean standard deviation of the vegetation index": mean_index_sd,
        "Mean standard deviation of the standard deviation vegetation index": sd_index_sd,

        # amplitudy
        "Total amplitude of vegetation index": A_total,
        "Total increase changes of vegetation index": A_pos,
        "Total decrease changes of vegetation index": A_neg,

        # procenty
        "Total relative vegetation index amplitude (%)": A_pct_total,
        "Total relative increase change of vegetation index amplitude (%)": A_pct_pos,
        "Total relative decrease change of vegetation index amplitude (%)": A_pct_neg,

        # częstość
        "Number of increase changes vegetation index": n_pos,
        "Number of decrease changes vegetation index": n_neg,

        # struktura
        "Roughness of vegetation index dynamics": J,
        "Concentration of vegetation index changes": C,

        # normalizacja
        "Total normalized temporal amplitude relative to index bounds": A_u,
        "Normalized temporal roughness relative to index bounds": J_u,

        # zależność poziom–ruch
        "Spearman correlation between index level and magnitude of temporal change": K
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

        y_mean = g[VALUE_COL_MEAN].values
        y_sd = g[VALUE_COL_SD].values

        if len(y_mean) < 2 or np.isnan(y_mean).any() or np.isnan(y_sd).any():
            continue

        metrics = compute_metrics(y_mean, y_sd)
        row = dict(zip(GROUP_COLS, keys))

        # Zamiana Name → custom label
        raw_name = row["Name"]
        row["Name"] = NAME_LABELS.get(raw_name, raw_name)

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
    if len(sys.argv) == 3:
        input_csv = sys.argv[1]
        output_csv = sys.argv[2]
        print("▶ Używam ścieżek z argumentów")
    else:
        input_csv = DEFAULT_INPUT_CSV
        output_csv = DEFAULT_OUTPUT_CSV
        print("▶ Używam domyślnych ścieżek")

    main(input_csv, output_csv)
