import os
import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox

def select_folder():
    folder = filedialog.askdirectory(title="Wybierz folder z plikami CSV")
    if folder:
        folder_entry.delete(0, tk.END)
        folder_entry.insert(0, folder)

def merge_csv():
    folder = folder_entry.get()
    measurement = measurement_entry.get().strip()
    altitude = altitude_entry.get().strip()

    if not folder:
        messagebox.showerror("Błąd", "Nie wybrano folderu")
        return
    if not measurement:
        messagebox.showerror("Błąd", "Nie wpisano nazwy / numeru pomiaru")
        return
    if not altitude:
        messagebox.showerror("Błąd", "Nie wpisano wysokości pułapu")
        return

    csv_files = [f for f in os.listdir(folder) if f.lower().endswith(".csv")]
    if not csv_files:
        messagebox.showerror("Błąd", "Brak plików CSV w folderze")
        return

    source_folder = os.path.basename(folder)
    merged = []

    for file in csv_files:
        file_path = os.path.join(folder, file)

        # Nazwa indeksu z nazwy pliku
        index_name = file.split("-annotation")[0]

        df = pd.read_csv(file_path)

        # DODAWANE KOLUMNY
        df["index_name"] = index_name
        df["source_folder"] = source_folder
        df["measurement"] = measurement
        df["altitude_m"] = altitude

        merged.append(df)

    final_df = pd.concat(merged, ignore_index=True)

    # AUTOMATYCZNA NAZWA PLIKU WYNIKOWEGO
    output_name = f"{source_folder}_merged.csv"
    output_path = os.path.join(folder, output_name)

    final_df.to_csv(output_path, index=False)

    messagebox.showinfo(
        "Gotowe",
        f"Scalono {len(csv_files)} plików\n"
        f"Liczba wierszy: {len(final_df)}\n\n"
        f"Plik zapisano jako:\n{output_path}"
    )

# =========================
# GUI
# =========================

root = tk.Tk()
root.title("Merge indeksów CSV")

frame = tk.Frame(root, padx=10, pady=10)
frame.pack()

# Folder
tk.Label(frame, text="Folder z plikami CSV:").grid(row=0, column=0, sticky="w")
folder_entry = tk.Entry(frame, width=60)
folder_entry.grid(row=1, column=0, padx=5, pady=5)
tk.Button(frame, text="Wybierz folder", command=select_folder)\
    .grid(row=1, column=1, padx=5)

# Pomiar
tk.Label(frame, text="Nazwa / numer pomiaru:").grid(row=2, column=0, sticky="w")
measurement_entry = tk.Entry(frame, width=30)
measurement_entry.grid(row=3, column=0, padx=5, pady=5, sticky="w")

# Pułap
tk.Label(frame, text="Wysokość pułapu (m):").grid(row=2, column=1, sticky="w")
altitude_entry = tk.Entry(frame, width=10)
altitude_entry.grid(row=3, column=1, padx=5, pady=5, sticky="w")

# Start
tk.Button(
    frame,
    text="Scal do jednego CSV",
    command=merge_csv,
    height=2
).grid(row=4, column=0, columnspan=2, pady=15)

root.mainloop()
