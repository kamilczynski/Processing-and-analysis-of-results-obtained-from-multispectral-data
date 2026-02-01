import pandas as pd
import re

# =======================
# PATHS
# =======================

INPUT_CSV = r"C:/.csv"
OUTPUT_CSV = r"C:/.csv"


# =======================
# AUXILIARY FUNCTIONS
# =======================

def parse_name(name):
    """
    Rozbija np. ENRO3malykwadrat na:
    cultivar = ENRO
    shoots = 3
    size = maly / duzy
    """
    m = re.match(r"(Enrosadira|Polonez)\s+(\d)\s+(Bounded|Edges)", name)
    if m:
        cultivar = m.group(1)
        shoots = int(m.group(2))
        size = m.group(3)
        return cultivar, size, shoots
    else:
        return None, None, None


# =======================
# SORT
# =======================

df = pd.read_csv(INPUT_CSV)

# break Name into logical columns
parsed = df["Name"].apply(parse_name)
df["cultivar"] = parsed.apply(lambda x: x[0])
df["size"] = parsed.apply(lambda x: x[1])
df["shoots"] = parsed.apply(lambda x: x[2])

# custom orders
cultivar_order = {"Enrosadira": 0, "Polonez": 1}
size_order = {"Bounded": 0, "Edges": 1}

df["cultivar_ord"] = df["cultivar"].map(cultivar_order)
df["size_ord"] = df["size"].map(size_order)

# KEY SORTS
df_sorted = df.sort_values(
    by=[
        "index_name",      # index
        "altitude_m",      # pitch
        "Type",            # annotation method
        "cultivar_ord",    # ENRO → POLO
        "size_ord",        # bounded → edges
        "shoots"           # 2 → 5
    ]
)

# clean
df_sorted = df_sorted.drop(columns=[
    "cultivar", "size", "shoots",
    "cultivar_ord", "size_ord"
])

df_sorted.to_csv(OUTPUT_CSV, index=False)

print("✔ Dane posortowane logicznie")
print("✔ Zapisano do:", OUTPUT_CSV)
