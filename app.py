import streamlit as st
import pandas as pd
from fpdf import FPDF
import datetime
import io

# ----------------------------
# KONFIGURASI LOGIN (BERDASARKAN NAMA)
# ----------------------------

AUTHORIZED_USERS = ["bagoes", "dimas", "iwan"]  # Semua huruf kecil untuk pencocokan

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.image("R2B.png", width=180)
    st.title("🔐 Login Pengguna")

    nama = st.text_input("Masukkan nama pengguna (contoh: Bagoes)").strip().lower()

    if st.button("Login"):
        if nama in AUTHORIZED_USERS:
            st.session_state.logged_in = True
            st.session_state.username = nama  # Simpan nama pengguna
            st.success(f"✅ Selamat datang, {nama.title()}!")
        else:
            st.error("❌ Nama tidak dikenali. Silakan coba lagi.")
    st.stop()

# ----------------------------
# MODE TEMA (DARK/LIGHT)
# ----------------------------
tema = st.sidebar.radio("🌗 Pilih Tema", ["Light", "Dark"])

if tema == "Dark":
    st.markdown("""
        <style>
            .main { background-color: #0e1117; color: white; }
            .stButton>button { background-color: #21262d; color: white; }
        </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
        <style>
            .main {
                background-color: #eaf3fa;
                color: #001f3f;
            }
            .stButton>button {
                background-color: #001f3f;
                color: #ffdc00;
                border: none;
                padding: 0.5em 1em;
                font-weight: bold;
                border-radius: 8px;
            }
        </style>
    """, unsafe_allow_html=True)

# ----------------------------
# DATA KEMASAN
# ----------------------------
kemasan_data = {
    "Bag Retort": {
        "8x9 cm": 630, "12x12 cm": 1390, "12x15 cm": 1400,
        "13x21 cm": 2000, "15x20 cm": 2300, "15x30 cm": 3300,
        "15x40 cm": 4350, "16x23 cm": 2400, "17x25 cm": 3700,
        "25x34 cm": 5400, "25x50 cm": 10500
    },
    "Standing Pouch": {
        "12x16 cm": 1700, "13x20,5 cm": 2100, "16x29 cm": 4000
    }
}

# ----------------------------
# INPUT DATA
# ----------------------------
st.sidebar.image("R2B.png", width=180)
st.sidebar.markdown("### 📊 Input Data Perhitungan HPP")

jenis_kemasan = st.sidebar.selectbox("Jenis Kemasan", list(kemasan_data.keys()) + ["Custom"])

if jenis_kemasan != "Custom":
    ukuran_kemasan = st.sidebar.selectbox("Ukuran Kemasan", list(kemasan_data[jenis_kemasan].keys()))
    harga_kemasan = kemasan_data[jenis_kemasan][ukuran_kemasan]
else:
    ukuran_kemasan = st.sidebar.text_input("Ukuran Custom (cth: 10x10 cm)")
    harga_kemasan = st.sidebar.number_input("Harga Custom per pcs", min_value=10, value=1000)

jumlah_kemasan = st.sidebar.number_input("Jumlah Produk Diproses", min_value=15, max_value=1000, value=50)
biaya_sewa_bulanan = st.sidebar.number_input("Biaya Sewa per Bulan", min_value=0, value=1000000)
periode_sewa_bulan = st.sidebar.slider("Periode Pembagian Biaya (bulan)", 1, 24, 12)

# Profit perusahaan
profit_persen = st.sidebar.slider("🧮 Target Profit Perusahaan (%)", min_value=20, max_value=150, value=30)

# ----------------------------
# PERHITUNGAN BIAYA
# ----------------------------
harga_gas_per_proses = 24000 / 4
pemakaian_air_liter = 80
harga_air_per_liter = 120000 / 500
harga_air_per_proses = harga_air_per_liter * pemakaian_air_liter

def hitung_listrik():
    freezer = (140 / 1000) * 24
    vacuum = (120 / 1000) * 2
    sealer = (500 / 1000) * 2
    lampu = (6 * 30 / 1000) * 5.5
    total_kwh = freezer + vacuum + sealer + lampu
    return total_kwh * 1500

biaya_listrik = hitung_listrik()
biaya_sewa_per_proses = biaya_sewa_bulanan / 30
biaya_total = (harga_kemasan * jumlah_kemasan) + harga_gas_per_proses + harga_air_per_proses + biaya_listrik + biaya_sewa_per_proses

pajak = biaya_total * 0.005
harga_setelah_pajak = biaya_total + pajak

laba_perusahaan = harga_setelah_pajak * (profit_persen / 100)
harga_jual_total = harga_setelah_pajak + laba_perusahaan
harga_jual_per_pcs = harga_jual_total / jumlah_kemasan
hpp_per_pcs = harga_setelah_pajak / jumlah_kemasan
margin_aktual = (laba_perusahaan / harga_setelah_pajak) * 100

# ----------------------------
# PERHITUNGAN FINAL
# ----------------------------

# Tambahkan Biaya Tenaga Kerja Harian
biaya_tenaga_kerja = 150_000

# Tambahkan Biaya Operasional 30%
biaya_operasional = biaya_total * 0.30

# Tambahkan Cadangan Operasional 10%
cadangan_operasional = biaya_total * 0.10

# Total Biaya Final setelah semua tambahan
biaya_total_final = biaya_total + biaya_operasional + cadangan_operasional + biaya_tenaga_kerja

# Pajak 0.5%
pajak = biaya_total_final * 0.005
biaya_setelah_pajak = biaya_total_final + pajak

# Hitung Harga Jual
harga_jual_total = biaya_setelah_pajak * (1 + profit_persen / 100)
harga_jual_per_pcs = harga_jual_total / jumlah_kemasan

# Hitung Laba dan Margin Aktual
laba_perusahaan = harga_jual_total - biaya_setelah_pajak
margin_aktual = (laba_perusahaan / biaya_setelah_pajak) * 100

# Hitung Target Jumlah Produk yang Harus Diproses
target_produk_retort = harga_jual_total // harga_jual_per_pcs

# Hitung Target Mingguan, Bulanan, 3 Bulanan
target_mingguan = int(target_produk_retort)
target_bulanan = target_mingguan * 4
target_3_bulanan = target_bulanan * 3

# ----------------------------
# OUTPUT TAMPILAN
# ----------------------------

st.title("💼 HPP Jasa Kemasan & Pengolahan Retort")

col1, col2 = st.columns(2)
col1.metric("📦 Biaya Produksi", f"Rp {biaya_total:,.0f}")
col2.metric("⚙️ Biaya Operasional (30%)", f"Rp {biaya_operasional:,.0f}")

col1, col2 = st.columns(2)
col1.metric("👷 Biaya Tenaga Kerja Harian", f"Rp {biaya_tenaga_kerja:,.0f}")
col2.metric("💼 Cadangan Operasional (10%)", f"Rp {cadangan_operasional:,.0f}")

st.metric("🧾 Total Biaya + Pajak", f"Rp {biaya_setelah_pajak:,.0f}")

col1, col2, col3 = st.columns(3)
col1.metric("💰 Harga Jual Total", f"Rp {harga_jual_total:,.0f}")
col2.metric("🧮 Harga Jual per Pcs", f"Rp {harga_jual_per_pcs:,.0f}")
col3.metric("📈 Laba Perusahaan", f"Rp {laba_perusahaan:,.0f}")

st.metric("🔁 Margin Aktual", f"{margin_aktual:.2f}%")

# Tambahan: Tampilkan Target Produksi
st.metric("🎯 Target Mingguan", f"{target_mingguan:,} pcs")
st.metric("📆 Target Bulanan", f"{target_bulanan:,} pcs")
st.metric("📅 Target 3 Bulan", f"{target_3_bulanan:,} pcs")

# ----------------------------
# PERBANDINGAN
# ----------------------------
st.markdown("### 📊 Ringkasan Perbandingan Harga")
st.write(f"- **Biaya Produksi Asli**: Rp {biaya_total:,.0f}")
st.write(f"- **+ Biaya Operasional (30%)**: Rp {biaya_operasional:,.0f}")
st.write(f"- **+ Biaya Tenaga Kerja**: Rp {biaya_tenaga_kerja:,.0f}")
st.write(f"- **+ Cadangan Operasional (10%)**: Rp {cadangan_operasional:,.0f}")
st.write(f"- **Total Biaya + Pajak (0.5%)**: Rp {biaya_setelah_pajak:,.0f}")
st.write(f"- **Harga Jual per pcs (dengan target profit {profit_persen}%)**: Rp {harga_jual_per_pcs:,.0f}")
st.write(f"- **Margin aktual**: {margin_aktual:.2f}%")

# ----------------------------
# GRAFIK VISUAL
# ----------------------------
st.markdown("### 📉 Grafik Komponen Biaya")
data_chart = {
    "Komponen": ["Produksi", "Operasional", "Cadangan", "Tenaga Kerja", "Pajak"],
    "Biaya (Rp)": [biaya_total, biaya_operasional, cadangan_operasional, biaya_tenaga_kerja, pajak],
}
df_chart = pd.DataFrame(data_chart)
st.bar_chart(df_chart.set_index("Komponen"))

# ----------------------------
# SARAN OTOMATIS BERDASARKAN DATA
# ----------------------------
st.markdown("### 🧠 Saran Otomatis")
saran = ""

if margin_aktual < 10:
    saran = "Margin sangat rendah. Pertimbangkan menaikkan harga jual atau menekan biaya."
elif 10 <= margin_aktual <= 20:
    saran = "Margin cukup, tetapi masih bisa dioptimalkan. Evaluasi efisiensi proses."
else:
    saran = "Margin sehat. Model usaha terlihat menguntungkan."

if harga_jual_per_pcs < 3000:
    saran += "\nHarga jual per pcs sangat rendah, pastikan tidak di bawah standar pasar."
elif harga_jual_per_pcs > 10000:
    saran += "\nHarga jual cukup tinggi, pastikan sesuai dengan value yang diterima pelanggan."

st.info(saran)

# ----------------------------
# EKSPOR DATA (PDF/CSV)
# ----------------------------

import io
import csv
from fpdf import FPDF

st.markdown("### 📤 Ekspor Laporan")

# CSV
csv_buffer = io.StringIO()
csv_writer = csv.writer(csv_buffer)
csv_writer.writerow(["Komponen", "Nilai"])
csv_writer.writerow(["Biaya Produksi", biaya_total])
csv_writer.writerow(["Biaya Operasional", biaya_operasional])
csv_writer.writerow(["Biaya Tenaga Kerja", biaya_tenaga_kerja])
csv_writer.writerow(["Cadangan Operasional", cadangan_operasional])
csv_writer.writerow(["Pajak", pajak])
csv_writer.writerow(["Total Biaya + Pajak", biaya_setelah_pajak])
csv_writer.writerow(["Harga Jual Total", harga_jual_total])
csv_writer.writerow(["Harga Jual per Pcs", harga_jual_per_pcs])
csv_writer.writerow(["Laba Perusahaan", laba_perusahaan])
csv_writer.writerow(["Margin Aktual", margin_aktual])
csv_writer.writerow(["Target Mingguan", target_mingguan])
csv_writer.writerow(["Target Bulanan", target_bulanan])
csv_writer.writerow(["Target 3 Bulan", target_3_bulanan])

st.download_button("⬇️ Download CSV", csv_buffer.getvalue(), file_name="laporan_hpp.csv", mime="text/csv")

# PDF
pdf = FPDF()
pdf.add_page()
pdf.set_font("Arial", size=12)
pdf.cell(200, 10, txt="Laporan HPP Retort", ln=True, align='C')
pdf.ln(10)

data_pdf = [
    ("Biaya Produksi", biaya_total),
    ("Biaya Operasional", biaya_operasional),
    ("Biaya Tenaga Kerja", biaya_tenaga_kerja),
    ("Cadangan Operasional", cadangan_operasional),
    ("Pajak", pajak),
    ("Total Biaya + Pajak", biaya_setelah_pajak),
    ("Harga Jual Total", harga_jual_total),
    ("Harga Jual per Pcs", harga_jual_per_pcs),
    ("Laba Perusahaan", laba_perusahaan),
    ("Margin Aktual", f"{margin_aktual:.2f}%"),
    ("Target Mingguan", target_mingguan),
    ("Target Bulanan", target_bulanan),
    ("Target 3 Bulan", target_3_bulanan),
]

for label, value in data_pdf:
    pdf.cell(200, 10, txt=f"{label}: Rp {value:,}" if isinstance(value, (int, float)) else f"{label}: {value}", ln=True)

pdf_output = io.BytesIO()
pdf.output(pdf_output)
pdf_output.seek(0)
st.download_button("⬇️ Download PDF", pdf_output, file_name="laporan_hpp.pdf", mime="application/pdf")


# ----------------------------
# RESET
# ----------------------------
if st.button("🔄 Reset"):
    for k in list(st.session_state.keys()):
        del st.session_state[k]
    st.rerun()
