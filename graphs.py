import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.ticker import FormatStrFormatter, MultipleLocator
import numpy as np

# --------------------------------
# PATHS
# --------------------------------
DATA_PATH = r"C:\Users\topgu\Desktop\Art\OSTATNIE ARTYKULY\ZAGESZCZENIE\WYNIKI zageszczenie\jesiennabigmerge.csv"
OUTPUT_DIR = r"C:\Users\topgu\Desktop\Art\OSTATNIE ARTYKULY\ZAGESZCZENIE\WYNIKI zageszczenie\WYKRESY JESIENNA STYCZEN\POCZWORNE JESIENNA ZAGESZCZENIE\GITHUB"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ======================================================
# USER CONFIG
# ======================================================
FONT_CONFIG = {
    "title": 12,
    "label": 12,
    "ticks": 10,
    "legend": 14
}

COMBINATION_LABELS = {
    "ENRO2malykwadrat": "Two canes",
    "ENRO3malykwadrat": "Three canes",
    "ENRO4malykwadrat": "Four canes",
    "ENRO5malykwadrat": "Five canes",
    "POLO2malykwadrat": "Two canes",
    "POLO3malykwadrat": "Three canes",
    "POLO4malykwadrat": "Four canes",
    "POLO5malykwadrat": "Five canes",
}

PALETTE = {
    "Two canes":   "#1B4F72",
    "Three canes": "#2E8B57",
    "Four canes":  "#E67E22",
    "Five canes":  "#7D3C98"
}

INDICES_4 = {
    "GNDVI":  "(a) GNDVI",
    "NDRE":   "(b) NDRE",
    "OSAVI":  "(c) OSAVI",
    "MCARI2": "(d) MCARI2",
}

# --- Y AXIS CONFIGURATION PER INDEX ---
Y_AXIS_CONFIG = {
    "GNDVI":  {"ylim": (0.550, 0.950), "step": 0.050},
    "NDRE":   {"ylim": (0.100, 0.500), "step": 0.050},
    "OSAVI":  {"ylim": (0.450, 0.850), "step": 0.050},
    "MCARI2": {"ylim": (0.500, 1.000), "step": 0.050},
}

# ======================================================
# STYLE
# ======================================================
sns.set_theme(context="paper", style="white", font_scale=1.1)

plt.rcParams.update({
    "figure.dpi": 300,
    "savefig.dpi": 600,
    "font.family": "DejaVu Sans",
    "axes.titlesize": FONT_CONFIG["title"],
    "axes.labelsize": FONT_CONFIG["label"],
    "xtick.labelsize": FONT_CONFIG["ticks"],
    "ytick.labelsize": FONT_CONFIG["ticks"],
    "legend.fontsize": FONT_CONFIG["legend"],
})

# --------------------------------
# LOAD DATA
# --------------------------------
df = pd.read_csv(DATA_PATH)

# --------------------------------
# CONSTANTS
# --------------------------------
ZESTAWY = {
    "ENRO_malykwadrat": [
        "ENRO2malykwadrat",
        "ENRO3malykwadrat",
        "ENRO4malykwadrat",
        "ENRO5malykwadrat",
    ],
    "POLO_malykwadrat": [
        "POLO2malykwadrat",
        "POLO3malykwadrat",
        "POLO4malykwadrat",
        "POLO5malykwadrat",
    ]
}

ALTITUDE = 30

# --------------------------------
# PLOTTING FUNCTION
# --------------------------------
def plot_4panel_indices(df, zestaw_name, zestaw, indices_dict, altitude):

    df_filt = df[
        (df["Name"].isin(zestaw)) &
        (df["index_name"].isin(indices_dict.keys())) &
        (df["altitude_m"] == altitude)
    ]

    if df_filt.empty:
        return

    fig, axes = plt.subplots(2, 2, figsize=(14, 10), sharex=True)
    axes = axes.flatten()

    for i, (ax, (index_key, index_label)) in enumerate(
        zip(axes, indices_dict.items())
    ):

        sub_idx = df_filt[df_filt["index_name"] == index_key]

        for name in zestaw:
            label = COMBINATION_LABELS[name]
            color = PALETTE[label]

            sub = sub_idx[sub_idx["Name"] == name].sort_values("measurement")
            if sub.empty:
                continue

            ax.plot(
                sub["measurement"],
                sub["Mean index value"],
                marker="o",
                linewidth=1.6,
                color=color,
                clip_on=False  # ← KLUCZ
            )

        # ---- TITLE
        ax.set_title(index_label, loc="left")

        # ---- Y AXIS (HARD, PUBLICATION-GRADE)
        cfg = Y_AXIS_CONFIG[index_key]
        ymin, ymax = cfg["ylim"]

        # HARD bounds (no renderer padding)
        ax.set_ybound(ymin, ymax)
        ax.set_ylim(ymin, ymax)
        ax.autoscale(False)
        ax.margins(y=0)

        # exact ticks including edges
        ax.set_yticks(
            np.arange(ymin, ymax + cfg["step"] / 2, cfg["step"])
        )

        ax.yaxis.set_major_formatter(FormatStrFormatter('%.3f'))

        # ---- X AXIS
        ax.set_xlim(df["measurement"].min(), df["measurement"].max())
        ax.set_xticks(
            range(
                int(df["measurement"].min()),
                int(df["measurement"].max()) + 1
            )
        )

        #ax.grid(axis="x", linestyle="--", linewidth=0.6, alpha=0.8)
        ax.grid(axis="y", linestyle="--", linewidth=0.6, alpha=0.8)

        # ---- AXIS LABELS
        if i % 2 == 0:
            ax.set_ylabel("Mean index value")
        if i >= 2:
            ax.set_xlabel("Measurement")

    # ---- LEGEND ----
    handles = [
        Line2D([0], [0], color=PALETTE[k], lw=8)
        for k in PALETTE
    ]

    fig.legend(
        handles,
        PALETTE.keys(),
        loc="lower center",
        ncol=4,
        frameon=False,
        bbox_to_anchor=(0.5, 0.02)  # ← IDEALNE CENTROWANIE
    )

    plt.tight_layout(rect=[0.01, 0.08, 1, 1])

    fname = f"{zestaw_name}_{altitude}m_4panel"
    plt.savefig(os.path.join(OUTPUT_DIR, fname + ".png"), dpi=600)
    plt.savefig(os.path.join(OUTPUT_DIR, fname + ".svg"))
    plt.close()

# --------------------------------
# GENERATE FIGURES
# --------------------------------
for zestaw_name, zestaw in ZESTAWY.items():
    plot_4panel_indices(
        df=df,
        zestaw_name=zestaw_name,
        zestaw=zestaw,
        indices_dict=INDICES_4,
        altitude=ALTITUDE
    )
