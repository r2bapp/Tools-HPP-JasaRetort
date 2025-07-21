import streamlit as st
import pandas as pd
from fpdf import FPDF
import datetime
import io

# ----------------------------
# KONFIGURASI LOGIN
# ----------------------------
AUTHORIZED_EMAIL = "rumahretortbersama1@gmail.com"

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.image("R2B.png", width=180)
    st.title("🔐 Login Pengguna")
    email = st.text_input("Masukkan email terdaftar")
    if st.button("Login"):
        if email.strip().lower() == AUTHORIZED_EMAIL:
            st.session_state.logged_in = True
            st.success("✅ Berhasil login!")
        else:
            st.error("❌ Email tidak dikenali.")
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
            .main { background-color: #f4f6fa; }
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
    harga_kemasan = st.sidebar.number_input("Harga Custom per pcs", min_value=100, value=1000)

jumlah_kemasan = st.sidebar.number_input("Jumlah Produk Diproses", min_value=15, max_value=100, value=50)
margin = st.sidebar.slider("Margin Keuntungan (%)", 0, 100, 20)
biaya_sewa_bulanan = st.sidebar.number_input("Biaya Sewa per Bulan", min_value=0, value=1000000)
periode_sewa_bulan = st.sidebar.slider("Periode Pembagian Biaya (bulan)", 1, 24, 12)

# ----------------------------
# PERHITUNGAN BIAYA
# ----------------------------
harga_gas_per_proses = 23000 / 5
pemakaian_air_liter = 70
harga_air_per_liter = 120000 / 500
harga_air_per_proses = harga_air_per_liter * pemakaian_air_liter

def hitung_listrik():
    freezer = (140 / 1000) * 24
    vacuum = (120 / 1000) * 2
    sealer = (500 / 1000) * 2
    lampu = (4 * 25 / 1000) * 5.5
    total_kwh = freezer + vacuum + sealer + lampu
    return total_kwh * 1500  # Tarif listrik/kWh

biaya_listrik = hitung_listrik()
biaya_sewa_per_proses = biaya_sewa_bulanan / 30

biaya_total = (harga_kemasan * jumlah_kemasan) + harga_gas_per_proses + harga_air_per_proses + biaya_listrik + biaya_sewa_per_proses
pajak = biaya_total * 0.005
harga_setelah_pajak = biaya_total + pajak
harga_dengan_margin = harga_setelah_pajak * (1 + margin / 100)
hpp_per_pcs = harga_dengan_margin / jumlah_kemasan

# ----------------------------
# OUTPUT TAMPILAN
# ----------------------------
st.title("💼 HPP Jasa Kemasan & Pengolahan Retort")

col1, col2, col3 = st.columns(3)
col1.metric("📦 Total Biaya", f"Rp {biaya_total:,.0f}")
col2.metric("💸 HPP per pcs", f"Rp {hpp_per_pcs:,.0f}")
col3.metric("💰 Harga Jual", f"Rp {hpp_per_pcs:,.0f}")

# ----------------------------
# EKSPOR CSV
# ----------------------------
if st.button("💾 Simpan CSV"):
    data = pd.DataFrame({
        "Ukuran Kemasan": [ukuran_kemasan],
        "Harga Kemasan": [harga_kemasan],
        "Jumlah": [jumlah_kemasan],
        "Biaya Total": [biaya_total],
        "Pajak": [pajak],
        "Harga per pcs": [hpp_per_pcs]
    })
    filename = f"data_hpp_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    data.to_csv(filename, index=False)
    st.success(f"✅ Disimpan sebagai {filename}")

# ----------------------------
# EKSPOR PDF
# ----------------------------
if st.button("📄 Export PDF"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, "Laporan HPP Jasa Retort", ln=True, align='C')
    pdf.set_font("Arial", '', 12)
    pdf.ln(10)
    pdf.cell(200, 10, f"Ukuran Kemasan: {ukuran_kemasan}", ln=True)
    pdf.cell(200, 10, f"Jumlah Produk: {jumlah_kemasan} pcs", ln=True)
    pdf.cell(200, 10, f"Total Biaya: Rp {biaya_total:,.0f}", ln=True)
    pdf.cell(200, 10, f"Pajak (0.5%): Rp {pajak:,.0f}", ln=True)
    pdf.cell(200, 10, f"Harga Jual per pcs: Rp {hpp_per_pcs:,.0f}", ln=True)

   # Simpan PDF ke buffer
buffer = io.BytesIO()
pdf.output(buffer)
buffer.seek(0)

# Tombol download PDF
st.download_button(
    label="📄 Download PDF",
    data=buffer,
    file_name="HPP_Retort.pdf",
    mime="application/pdf"
)

# ----------------------------
# RESET
# ----------------------------
if st.button("🔄 Reset"):
    for k in list(st.session_state.keys()):
        del st.session_state[k]
    st.rerun()
