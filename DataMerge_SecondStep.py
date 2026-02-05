import os
import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox

def select_input_folder():
    folder = filedialog.askdirectory(title="Select the folder with the CSV files")
    if folder:
        input_entry.delete(0, tk.END)
        input_entry.insert(0, folder)

def select_output_file():
    file = filedialog.asksaveasfilename(
        title="Save the resulting CSV file",
        defaultextension=".csv",
        filetypes=[("CSV", "*.csv")]
    )
    if file:
        output_entry.delete(0, tk.END)
        output_entry.insert(0, file)

def merge_all():
    input_folder = input_entry.get()
    output_file = output_entry.get()

    if not input_folder:
        messagebox.showerror("Error", "No input folder selected")
        return
    if not output_file:
        messagebox.showerror("Error", "No output file selected")
        return

    csv_files = [
        f for f in os.listdir(input_folder)
        if f.lower().endswith(".csv")
    ]

    if not csv_files:
        messagebox.showerror("Error", "No CSV files in the folder")
        return

    merged = []

    for file in csv_files:
        file_path = os.path.join(input_folder, file)
        df = pd.read_csv(file_path)
        merged.append(df)

    final_df = pd.concat(merged, ignore_index=True)

    final_df.to_csv(output_file, index=False)

    messagebox.showinfo(
        "Ready",
        f"Merged {len(csv_files)} files\n"
        f"Number of rows: {len(final_df)}\n\n"
        f"Save to:\n{output_file}"
    )

# =========================
# GUI
# =========================

root = tk.Tk()
root.title("Merge all CSV files")

frame = tk.Frame(root, padx=10, pady=10)
frame.pack()

# Folder wejściowy
tk.Label(frame, text="Folder with CSV files:").grid(row=0, column=0, sticky="w")
input_entry = tk.Entry(frame, width=60)
input_entry.grid(row=1, column=0, padx=5, pady=5)
tk.Button(frame, text="Select folder", command=select_input_folder)\
    .grid(row=1, column=1, padx=5)

# Plik wyjściowy
tk.Label(frame, text="CSV output file:").grid(row=2, column=0, sticky="w")
output_entry = tk.Entry(frame, width=60)
output_entry.grid(row=3, column=0, padx=5, pady=5)
tk.Button(frame, text="Select file", command=select_output_file)\
    .grid(row=3, column=1, padx=5)

# Start
tk.Button(
    frame,
    text="Merge all into one CSV",
    command=merge_all,
    height=2
).grid(row=4, column=0, columnspan=2, pady=15)

root.mainloop()
