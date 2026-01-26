import pandas as pd
import re

# =======================
# ŚCIEŻKI
# =======================

INPUT_CSV = r"C:/Users/topgu/Desktop/Art/OSTATNIE ARTYKULY/ZAGESZCZENIE/WYNIKI zageszczenie/wyniki_dynamika.csv"
OUTPUT_CSV = r"C:/Users/topgu/Desktop/Art/OSTATNIE ARTYKULY/ZAGESZCZENIE/WYNIKI zageszczenie/wyniki_dynamika_SORTED.csv"


# =======================
# FUNKCJE POMOCNICZE
# =======================

def parse_name(name):
    """
    Rozbija np. ENRO3malykwadrat na:
    cultivar = ENRO
    shoots = 3
    size = maly / duzy
    """
    m = re.match(r"(ENRO|POLO)(\d)(maly|duzy)kwadrat", name)
    if m:
        cultivar = m.group(1)
        shoots = int(m.group(2))
        size = m.group(3)
        return cultivar, size, shoots
    else:
        return None, None, None


# =======================
# SORTOWANIE
# =======================

df = pd.read_csv(INPUT_CSV)

# rozbij Name na kolumny logiczne
parsed = df["Name"].apply(parse_name)
df["cultivar"] = parsed.apply(lambda x: x[0])
df["size"] = parsed.apply(lambda x: x[1])
df["shoots"] = parsed.apply(lambda x: x[2])

# kolejności niestandardowe
cultivar_order = {"ENRO": 0, "POLO": 1}
size_order = {"maly": 0, "duzy": 1}

df["cultivar_ord"] = df["cultivar"].map(cultivar_order)
df["size_ord"] = df["size"].map(size_order)

# SORT KLUCZOWY
df_sorted = df.sort_values(
    by=[
        "index_name",      # wskaźnik
        "altitude_m",      # pułap
        "Type",            # metoda adnotacji
        "cultivar_ord",    # ENRO → POLO
        "size_ord",        # mały → duży
        "shoots"           # 2 → 5
    ]
)

# sprzątanie
df_sorted = df_sorted.drop(columns=[
    "cultivar", "size", "shoots",
    "cultivar_ord", "size_ord"
])

df_sorted.to_csv(OUTPUT_CSV, index=False)

print("✔ Dane posortowane logicznie")
print("✔ Zapisano do:", OUTPUT_CSV)
