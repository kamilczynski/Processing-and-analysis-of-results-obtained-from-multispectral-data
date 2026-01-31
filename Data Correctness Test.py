import pandas as pd, numpy as np

df = pd.read_csv("C:/.csv")
GROUP_COLS = ["Name","index_name","altitude_m","Type"]

expected = set(range(1,12))
bad = []

for k,g in df.groupby(GROUP_COLS):
    s = set(g["measurement"].unique())
    if s != expected:
        bad.append((k, sorted(s)))

print("number of groups:", df.groupby(GROUP_COLS).ngroups)
print("groups with gaps:", len(bad))
