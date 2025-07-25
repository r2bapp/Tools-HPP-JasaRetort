import streamlit as st
import pandas as pd
from fpdf import FPDF
import datetime
import io

# ----------------------------
# KONFIGURASI LOGIN (BERDASARKAN NAMA)
# ----------------------------

AUTHORIZED_USERS = ["bagoes", "dimas", "iwan"]

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.image("R2B.png", width=180)
    st.title("🔐 Login Pengguna")

    nama = st.text_input("Masukkan nama pengguna (contoh: Bagoes)").strip().lower()

    if st.button("Login"):
        if nama in AUTHORIZED_USERS:
            st.session_state.logged_in = True
            st.session_state.username = nama
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

biaya_tenaga_kerja = 150_000
biaya_operasional = biaya_total * 0.30
cadangan_operasional = biaya_total * 0.10
biaya_total_final = biaya_total + biaya_operasional + cadangan_operasional + biaya_tenaga_kerja

pajak = biaya_total_final * 0.005
biaya_setelah_pajak = biaya_total_final + pajak

harga_jual_total = biaya_setelah_pajak * (1 + profit_persen / 100)
harga_jual_per_pcs = harga_jual_total / jumlah_kemasan

laba_perusahaan = harga_jual_total - biaya_setelah_pajak
profit_bersih = laba_perusahaan
profit_kotor = harga_jual_total - biaya_total
margin_aktual = (profit_bersih / biaya_setelah_pajak) * 100

# Target retort realistis
harga_per_proses = harga_jual_per_pcs * jumlah_kemasan

retort_per_hari = int((biaya_total_final * 1.2) / harga_per_proses)
retort_per_minggu = retort_per_hari * 7
retort_per_bulan = retort_per_hari * 30
retort_per_3bulan = retort_per_bulan * 3

# ----------------------------
# OUTPUT
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

st.metric("📊 Margin Aktual", f"{margin_aktual:.2f}%")

st.markdown("### 🎯 Target Proses Retort")
st.write(f"- Per Hari: {retort_per_hari} batch")
st.write(f"- Per Minggu: {retort_per_minggu} batch")
st.write(f"- Per Bulan: {retort_per_bulan} batch")
st.write(f"- Per 3 Bulan: {retort_per_3bulan} batch")

st.markdown("### 📍 Profitabilitas")
st.write(f"- 💵 Profit Kotor: Rp {profit_kotor:,.0f}")
st.write(f"- 💼 Profit Bersih: Rp {profit_bersih:,.0f}")

# Insight Otomatis
st.markdown("### 🤖 Insight Otomatis Berbasis Data")
if margin_aktual < profit_persen:
    st.warning("⚠️ Margin lebih kecil dari target profit. Pertimbangkan menaikkan harga atau efisiensi biaya.")
if biaya_operasional > biaya_total * 0.35:
    st.warning("⚠️ Biaya operasional cukup tinggi. Periksa kembali efisiensi penggunaan sumber daya.")
if harga_jual_per_pcs > 10000:
    st.info("💡 Harga jual per pcs tinggi, pastikan target pasar sesuai dengan pricing.")
else:
    st.success("✅ Biaya dan margin terlihat sehat untuk model bisnis saat ini.")
