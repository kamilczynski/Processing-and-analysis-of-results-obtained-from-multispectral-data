import os
import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox

def select_folder():
    folder = filedialog.askdirectory(title="Select the folder with the CSV files")
    if folder:
        folder_entry.delete(0, tk.END)
        folder_entry.insert(0, folder)

def merge_csv():
    folder = folder_entry.get()
    measurement = measurement_entry.get().strip()
    altitude = altitude_entry.get().strip()

    if not folder:
        messagebox.showerror("Error", "Nie wybrano folderu")
        return
    if not measurement:
        messagebox.showerror("Error", "No measurement name/number entered")
        return
    if not altitude:
        messagebox.showerror("Error", "No ceiling height entered")
        return

    csv_files = [f for f in os.listdir(folder) if f.lower().endswith(".csv")]
    if not csv_files:
        messagebox.showerror("Error", "No CSV files in the folder")
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
        "Ready",
        f"Merged {len(csv_files)} files\n"
        f"Number of rows: {len(final_df)}\n\n"
        f"File saved as:\n{output_path}"
    )

# =========================
# GUI
# =========================

root = tk.Tk()
root.title("Merge CSV indexes")

frame = tk.Frame(root, padx=10, pady=10)
frame.pack()

# Folder
tk.Label(frame, text="Folder with CSV files:").grid(row=0, column=0, sticky="w")
folder_entry = tk.Entry(frame, width=60)
folder_entry.grid(row=1, column=0, padx=5, pady=5)
tk.Button(frame, text="Select folder", command=select_folder)\
    .grid(row=1, column=1, padx=5)

# Pomiar
tk.Label(frame, text="Measurement name/number:").grid(row=2, column=0, sticky="w")
measurement_entry = tk.Entry(frame, width=30)
measurement_entry.grid(row=3, column=0, padx=5, pady=5, sticky="w")

# Pułap
tk.Label(frame, text="Flight ceiling (m):").grid(row=2, column=1, sticky="w")
altitude_entry = tk.Entry(frame, width=10)
altitude_entry.grid(row=3, column=1, padx=5, pady=5, sticky="w")

# Start
tk.Button(
    frame,
    text="Merge into one CSV",
    command=merge_csv,
    height=2
).grid(row=4, column=0, columnspan=2, pady=15)

root.mainloop()
