
import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk

DB_NAME = "prediksi_diabetes.db"

# ==========================================
# LAYER DATA (DATABASE & LOGIKA PREDIKSI)
# ==========================================


def run_query(sql, params=()):
  """Fungsi helper untuk menjalankan query SQLite secara aman[cite: 2]."""
  conn = sqlite3.connect(DB_NAME)
  try:
    with conn:
      return conn.execute(sql, params).fetchall()
  finally:
    conn.close()


def init_db():
  """Membuat database dan tabel prediksi_diabetes jika belum ada[cite: 1, 2]."""
  run_query("""
        CREATE TABLE IF NOT EXISTS prediksi_diabetes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nama_pasien TEXT NOT NULL,
            usia INTEGER NOT NULL,
            gula_darah REAL NOT NULL,
            bmi REAL NOT NULL,
            riwayat_ortu TEXT NOT NULL,
            hasil_prediksi TEXT NOT NULL
        )
    """)


def hitung_prediksi(gula_darah, bmi, riwayat_ortu):
  """Menentukan tingkat risiko diabetes berdasarkan aturan ketentuan."""
  if gula_darah >= 200:
    return "Risiko Tinggi / Sangat Tinggi", "#e53e3e" 
  elif 140 <= gula_darah <= 199:
    if bmi >= 30 or riwayat_ortu == "Ya":
      return "Risiko Tinggi", "#dd6b20"  
    else:
      return "Risiko Sedang", "#d69e2e"  
  else:  
    if bmi >= 30:
      return "Risiko Waspada / Sedang", "#dd6b20"
    elif riwayat_ortu == "Ya":
      return "Risiko Waspada", "#b7791f"
    else:
      return "Risiko Rendah", "#38a169"  


def tambah_pasien(nama, usia, gula_darah, bmi, riwayat_ortu, hasil_prediksi):
  run_query(
      """
        INSERT INTO prediksi_diabetes (nama_pasien, usia, gula_darah, bmi, riwayat_ortu, hasil_prediksi)
        VALUES (?, ?, ?, ?, ?, ?)
    """,
      (nama, usia, gula_darah, bmi, riwayat_ortu, hasil_prediksi),
  )


def ambil_semua_pasien(keyword=""):
  if keyword:
    return run_query(
        """
            SELECT id, nama_pasien, usia, gula_darah, bmi, riwayat_ortu, hasil_prediksi 
            FROM prediksi_diabetes WHERE nama_pasien LIKE ? ORDER BY id DESC
        """,
        (f"%{keyword}%",),
    )
  return run_query("""
        SELECT id, nama_pasien, usia, gula_darah, bmi, riwayat_ortu, hasil_prediksi 
        FROM prediksi_diabetes ORDER BY id DESC
    """)


def hapus_pasien(pasien_id):
  run_query("DELETE FROM prediksi_diabetes WHERE id = ?", (pasien_id,))


init_db()

root = tk.Tk()
root.title("Medical Diagnostic - Sistem Prediksi Risiko Diabetes")
root.geometry("900x680")
root.config(bg="#f8fafc")

COLOR_PRIMARY = "#1e3a8a"  
COLOR_SECONDARY = "#0f766e"  
COLOR_BG = "#f8fafc"
COLOR_CARD = "#ffffff"

header_frame = tk.Frame(root, bg=COLOR_PRIMARY, pady=15)
header_frame.pack(fill="x")

lbl_judul = tk.Label(
    header_frame,
    text="Aplikasi Prediksi Risiko Diabetes",
    font=("Segoe UI", 18, "bold"),
    bg=COLOR_PRIMARY,
    fg="white",
)
lbl_judul.pack()

lbl_sub = tk.Label(
    header_frame,
    text="Sistem Pakar Sederhana Berbasis GUI & SQLite Database",
    font=("Segoe UI", 10),
    bg=COLOR_PRIMARY,
    fg="#cbd5e1",
)
lbl_sub.pack()

main_frame = tk.Frame(root, bg=COLOR_BG)
main_frame.pack(fill="both", expand=True, padx=20, pady=15)

frame_form = tk.LabelFrame(
    main_frame,
    text=" Input Data Pasien ",
    font=("Segoe UI", 11, "bold"),
    bg=COLOR_CARD,
    fg=COLOR_PRIMARY,
    padx=15,
    pady=15,
)
frame_form.pack(side="left", fill="both", expand=False, padx=(0, 10))

entries = {}
fields = [
    ("Nama Pasien", "entry"),
    ("Usia (Tahun)", "entry"),
    ("Kadar Gula Darah (mg/dL)", "entry"),
    ("BMI (Indeks Massa Tubuh)", "entry"),
    ("Riwayat Diabetes Orang Tua", "combo"),
]

for i, (field, tipe) in enumerate(fields):
  lbl = tk.Label(
      frame_form,
      text=field + ":",
      font=("Segoe UI", 9, "bold"),
      bg=COLOR_CARD,
      anchor="w",
  )
  lbl.grid(row=i, column=0, sticky="w", pady=6)

  if tipe == "entry":
    ent = tk.Entry(
        frame_form, width=25, font=("Segoe UI", 10), relief="solid", bd=1
    )
    ent.grid(row=i, column=1, padx=10, pady=6, sticky="w")
    entries[field] = ent
  elif tipe == "combo":
    combo = ttk.Combobox(
        frame_form, values=["Ya", "Tidak"], width=23, state="readonly"
    )
    combo.grid(row=i, column=1, padx=10, pady=6, sticky="w")
    combo.set("Tidak")
    entries[field] = combo

frame_hasil = tk.Frame(frame_form, bg="#e2e8f0", bd=1, relief="solid")
frame_hasil.grid(
    row=len(fields), column=0, columnspan=2, sticky="ew", pady=(15, 10)
)

lbl_hasil_title = tk.Label(
    frame_hasil,
    text="HASIL PREDIKSI:",
    font=("Segoe UI", 9, "bold"),
    bg="#e2e8f0",
    fg="#475569",
)
lbl_hasil_title.pack(anchor="w", padx=10, pady=(5, 0))

lbl_hasil_value = tk.Label(
    frame_hasil,
    text="Menunggu Input Data...",
    font=("Segoe UI", 11, "bold"),
    bg="#e2e8f0",
    fg="#334155",
    wraplength=280,
    justify="left",
)
lbl_hasil_value.pack(anchor="w", padx=10, pady=(2, 8))

def baca_form():
  nama = entries["Nama Pasien"].get().strip()
  usia_str = entries["Usia (Tahun)"].get().strip()
  gula_str = entries["Kadar Gula Darah (mg/dL)"].get().strip()
  bmi_str = entries["BMI (Indeks Massa Tubuh)"].get().strip()
  riwayat = entries["Riwayat Diabetes Orang Tua"].get()

  if not nama or not usia_str or not gula_str or not bmi_str:
    messagebox.showwarning("Peringatan", "Semua kolom data wajib diisi!")
    return None

  try:
    usia = int(usia_str)
    gula_darah = float(gula_str)
    bmi = float(bmi_str)
  except ValueError:
    messagebox.showerror(
        "Error Format",
        "Usia, Gula Darah, dan BMI harus diisi dengan format angka!",
    )
    return None

  if usia <= 0 or gula_darah < 0 or bmi < 0:
    messagebox.showwarning(
        "Peringatan", "Nilai tidak boleh bernilai negatif atau nol!"
    )
    return None

  return nama, usia, gula_darah, bmi, riwayat


def proses_prediksi():
  data = baca_form()
  if data:
    nama, usia, gula_darah, bmi, riwayat = data
    hasil, warna = hitung_prediksi(gula_darah, bmi, riwayat)

    tambah_pasien(nama, usia, gula_darah, bmi, riwayat, hasil)

    frame_hasil.config(bg=warna)
    lbl_hasil_title.config(bg=warna, fg="white")
    lbl_hasil_value.config(
        text=f"{hasil}\n(Gula: {gula_darah} mg/dL | BMI: {bmi})",
        bg=warna,
        fg="white",
    )

    messagebox.showinfo(
        "Berhasil",
        f"Data pasien atas nama '{nama}' berhasil dianalisis & disimpan!",
    )
    muat_tabel()


def clear_form():
  entries["Nama Pasien"].delete(0, tk.END)
  entries["Usia (Tahun)"].delete(0, tk.END)
  entries["Kadar Gula Darah (mg/dL)"].delete(0, tk.END)
  entries["BMI (Indeks Massa Tubuh)"].delete(0, tk.END)
  entries["Riwayat Diabetes Orang Tua"].set("Tidak")
  frame_hasil.config(bg="#e2e8f0")
  lbl_hasil_title.config(bg="#e2e8f0", fg="#475569")
  lbl_hasil_value.config(
      text="Menunggu Input Data...", bg="#e2e8f0", fg="#334155"
  )


btn_proses = tk.Button(
    frame_form,
    text="Proses & Simpan Data",
    command=proses_prediksi,
    bg=COLOR_PRIMARY,
    fg="white",
    font=("Segoe UI", 9, "bold"),
    relief="flat",
    cursor="hand2",
    pady=6,
)
btn_proses.grid(row=len(fields) + 1, column=0, columnspan=2, sticky="ew", pady=4)

btn_clear = tk.Button(
    frame_form,
    text="Reset Form",
    command=clear_form,
    bg="#64748b",
    fg="white",
    font=("Segoe UI", 9, "bold"),
    relief="flat",
    cursor="hand2",
    pady=6,
)
btn_clear.grid(row=len(fields) + 2, column=0, columnspan=2, sticky="ew", pady=2)


frame_kanan = tk.Frame(main_frame, bg=COLOR_BG)
frame_kanan.pack(side="right", fill="both", expand=True)

frame_control = tk.Frame(frame_kanan, bg=COLOR_BG)
frame_control.pack(fill="x", pady=(0, 10))

lbl_search = tk.Label(
    frame_control, text="Cari Pasien:", font=("Segoe UI", 9), bg=COLOR_BG
)
lbl_search.pack(side="left", padx=(0, 5))

entry_search = tk.Entry(
    frame_control, font=("Segoe UI", 9), width=18, relief="solid", bd=1
)
entry_search.pack(side="left", padx=(0, 5))


def cari_data():
  keyword = entry_search.get().strip()
  muat_tabel(keyword)


btn_search = tk.Button(
    frame_control,
    text="Filter",
    command=cari_data,
    bg=COLOR_SECONDARY,
    fg="white",
    font=("Segoe UI", 8, "bold"),
    relief="flat",
)
btn_search.pack(side="left")


def hapus_terpilih():
  selected_item = tree.selection()
  if not selected_item:
    messagebox.showwarning(
        "Peringatan", "Pilih baris data pada tabel yang ingin dihapus terlebih dahulu!"
    )
    return

  item_data = tree.item(selected_item[0])["values"]
  pasien_id = item_data[0]
  nama = item_data[1]

  if messagebox.askyesno(
      "Konfirmasi Hapus",
      f"Apakah Anda yakin ingin menghapus data rekam medis pasien {nama}?",
  ):
    hapus_pasien(pasien_id)
    messagebox.showinfo("Sukses", "Data berhasil dihapus dari database.")
    muat_tabel()
    clear_form()


btn_hapus = tk.Button(
    frame_control,
    text="Hapus Terpilih",
    command=hapus_terpilih,
    bg="#dc2626",
    fg="white",
    font=("Segoe UI", 8, "bold"),
    relief="flat",
)
btn_hapus.pack(side="right")

cols = (
    "id",
    "nama_pasien",
    "usia",
    "gula_darah",
    "bmi",
    "riwayat_ortu",
    "hasil_prediksi",
)
tree = ttk.Treeview(frame_kanan, columns=cols, show="headings", height=18)

headers = ["ID", "Nama Pasien", "Usia", "Gula Darah", "BMI", "Ortu", "Prediksi Risiko"]
widths = [35, 110, 45, 75, 50, 55, 120]

for c, h, w in zip(cols, headers, widths):
  tree.heading(c, text=h)
  tree.column(c, width=w, anchor="center")

scrollbar = ttk.Scrollbar(
    frame_kanan, orient="vertical", command=tree.yview
)
tree.configure(yscrollcommand=scrollbar.set)

tree.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")


def muat_tabel(keyword=""):
  for row in tree.get_children():
    tree.delete(row)
  for row in ambil_semua_pasien(keyword):
    tree.insert("", tk.END, values=row)


def on_row_select(event):
  selected_item = tree.selection()
  if selected_item:
    item_data = tree.item(selected_item[0])["values"]
    clear_form()
    entries["Nama Pasien"].insert(0, item_data[1])
    entries["Usia (Tahun)"].insert(0, item_data[2])
    entries["Kadar Gula Darah (mg/dL)"].insert(0, item_data[3])
    entries["BMI (Indeks Massa Tubuh)"].insert(0, item_data[4])
    entries["Riwayat Diabetes Orang Tua"].set(item_data[5])
    lbl_hasil_value.config(text=f"Terpilih: {item_data[6]}")


tree.bind("<<TreeviewSelect>>", on_row_select)

muat_tabel()

root.mainloop()