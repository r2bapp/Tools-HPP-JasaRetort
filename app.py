# HPP Retort Streamlit App (Rebuild based on latest specification)

import streamlit as st
import pandas as pd
from fpdf import FPDF
import os

# ---------------------- SETUP ----------------------
st.set_page_config(page_title="HPP Jasa Kemas dan Pengawetan Retort", layout="centered")

st.markdown("""
<style>
body { background-color: #F9FAFB; }
.reportview-container .markdown-text-container {
    font-family: 'Segoe UI', sans-serif;
    color: #1F2937;
}
[data-testid="stSidebar"] > div:first-child {
    background-color: #0D1B2A;
    color: white;
}
</style>
""", unsafe_allow_html=True)

# ---------------------- USER AUTH ----------------------
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔒 Login")
    email = st.text_input("Masukkan Email Terdaftar")
    if st.button("Login"):
        if email.strip() == "rumahretortbersama1@gmail.com":
            st.session_state.authenticated = True
            st.experimental_rerun()
        else:
            st.error("Email tidak terdaftar. Hubungi admin.")
    st.stop()

# ---------------------- DATA ----------------------
kemasan_data = {
    "Retort Bag": {
        "8x9 cm": 630,
        "12x12 cm": 1390,
        "12x15 cm": 1400,
        "13x21 cm": 2000,
        "15x20 cm": 2300,
        "15x30 cm": 3300,
        "15x40 cm": 4350,
        "16x23 cm": 2400,
        "17x25 cm": 3700,
        "25x34 cm": 5400,
        "25x50 cm": 10500,
    },
    "Standing Pouch": {
        "12x16 cm": 1700,
        "13x20.5 cm": 2100,
        "16x29 cm": 4000,
    }
}

# ---------------------- INPUT FORM ----------------------
st.title("📊 HPP Jasa Kemas dan Pengawetan dengan Retort")
st.markdown("### Input Data Produksi")

kemasan_type = st.selectbox("Jenis Kemasan", list(kemasan_data.keys()) + ["Custom"])

if kemasan_type != "Custom":
    ukuran = st.selectbox("Ukuran", list(kemasan_data[kemasan_type].keys()))
    harga_kemasan = kemasan_data[kemasan_type][ukuran]
else:
    ukuran = st.text_input("Ukuran Custom")
    harga_kemasan = st.number_input("Harga per Pcs (Rp)", min_value=0, step=100)

jumlah_produk = st.number_input("Jumlah Produk (pcs)", min_value=15, max_value=100, step=1, value=15)

margin = st.slider("Margin Keuntungan (%)", 0, 100, 30)

# ---------------------- PERHITUNGAN HPP ----------------------
if st.button("Hitung HPP"):
    # Energi dan air per proses
    gas = 23000 / 5
    air = (120000 / 500) * 80

    listrik_per_jam = ((140 + 120 + 500 + 4 * 25) / 1000) * 1.5 * 1500  # 1.5 jam rata-rata, Rp1500/kWh

    total_biaya = (harga_kemasan * jumlah_produk) + gas + listrik_per_jam + air
    pajak = total_biaya * 0.005
    total_dengan_pajak = total_biaya + pajak
    hpp_per_pcs = total_dengan_pajak / jumlah_produk
    harga_jual = hpp_per_pcs * (1 + margin / 100)

    st.success("### Hasil Perhitungan")
    st.write(f"**Total Biaya Produksi:** Rp {total_biaya:,.0f}")
    st.write(f"**Pajak (0.5%):** Rp {pajak:,.0f}")
    st.write(f"**HPP per pcs:** Rp {hpp_per_pcs:,.0f}")
    st.write(f"**Harga Jual disarankan (dengan margin {margin}%):** Rp {harga_jual:,.0f}")

    # Simpan ke CSV
    df = pd.DataFrame({
        "Jenis Kemasan": [kemasan_type],
        "Ukuran": [ukuran],
        "Jumlah Produk": [jumlah_produk],
        "Harga Kemasan per pcs": [harga_kemasan],
        "Biaya Gas": [gas],
        "Biaya Air": [air],
        "Biaya Listrik": [listrik_per_jam],
        "Pajak": [pajak],
        "Total Biaya": [total_dengan_pajak],
        "HPP per pcs": [hpp_per_pcs],
        "Harga Jual": [harga_jual]
    })
    df.to_csv("hasil_perhitungan.csv", index=False)
    st.success("Data berhasil disimpan sebagai CSV.")

    # Export PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Hasil Perhitungan HPP Retort", ln=True, align='C')
    pdf.ln(10)
    for col in df.columns:
        pdf.cell(100, 10, f"{col}: {df[col][0]}", ln=True)

    pdf.output("hasil_perhitungan.pdf")
    st.download_button("📥 Download PDF", data=open("hasil_perhitungan.pdf", "rb"), file_name="hasil_HPP_Retort.pdf")

# ---------------------- RESET ----------------------
if st.button("Reset Data"):
    if os.path.exists("hasil_perhitungan.csv"):
        os.remove("hasil_perhitungan.csv")
    if os.path.exists("hasil_perhitungan.pdf"):
        os.remove("hasil_perhitungan.pdf")
    st.success("Data berhasil direset.")
