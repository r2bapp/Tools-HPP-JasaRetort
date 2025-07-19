import streamlit as st
import pandas as pd
import datetime
import os

st.set_page_config(page_title="HPP Retort", layout="centered")
st.title("🧮 HPP Retort - Harga Pokok Produksi Jasa Kemas & Retort")

# ---------------- AUTH ----------------
AUTHORIZED_EMAIL = "rumahretortbersama1@gmail.com"

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    email = st.text_input("Masukkan Email untuk Akses:", type="default")
    if st.button("Login"):
        if email.lower() == AUTHORIZED_EMAIL:
            st.session_state.authenticated = True
            st.success("Login berhasil!")
        else:
            st.error("Email tidak diizinkan.")
    st.stop()

# ---------------- DATA ----------------
kemasan_options = {
    "8x9 cm (Rp 630)": 630,
    "12x12 cm (Rp 1.390)": 1390,
    "12x15 cm (Rp 1.400)": 1400,
    "13x21 cm (Rp 2.000)": 2000,
    "15x20 cm (Rp 2.300)": 2300,
    "15x30 cm (Rp 3.300)": 3300,
    "15x40 cm (Rp 4.350)": 4350,
    "16x23 cm (Rp 2.400)": 2400,
    "17x25 cm (Rp 3.700)": 3700,
    "25x34 cm (Rp 5.400)": 5400,
    "25x50 cm (Rp 10.500)": 10500,
    "Standing 12x16 cm (Rp 1.700)": 1700,
    "Standing 13x20.5 cm (Rp 2.100)": 2100,
    "Standing 16x29 cm (Rp 4.000)": 4000,
    "Custom": None
}

# ---------------- FORM INPUT ----------------
with st.form("hpp_form"):
    st.subheader("📦 Pilih Kemasan")
    selected_kemasan = st.selectbox("Jenis Kemasan:", options=list(kemasan_options.keys()))
    if selected_kemasan == "Custom":
        harga_kemasan = st.number_input("Masukkan Harga Kemasan (Rp):", min_value=100)
    else:
        harga_kemasan = kemasan_options[selected_kemasan]

    st.subheader("⚡ Energi & Air")
    proses_retort = st.number_input("Jumlah Proses Retort (per 3kg gas):", min_value=1, value=1)
    listrik_jam = st.slider("Jam Pemakaian Listrik Total:", 1, 24, 3)
    air_liter = st.slider("Air Digunakan (liter):", 50, 500, 80)

    st.subheader("💰 Margin Keuntungan")
    margin = st.slider("Margin (%)", 0, 100, 30)

    submitted = st.form_submit_button("🔍 Hitung HPP & Harga Jual")

# ---------------- PERHITUNGAN ----------------
if submitted:
    gas_harga = 23000 / 4 * proses_retort
    listrik_watt = 140 + 120 + 500 + (6 * 25)
    listrik_kwh = listrik_watt / 1000 * listrik_jam
    listrik_harga = listrik_kwh * 1500  # Asumsi 1500/kWh
    air_harga = (air_liter / 500) * 120000

    subtotal = harga_kemasan + gas_harga + listrik_harga + air_harga
    pajak = subtotal * 0.005
    hpp = subtotal + pajak
    harga_jual = hpp + (hpp * margin / 100)

    # ---------------- OUTPUT ----------------
    st.success("✅ Perhitungan Selesai")
    st.metric("HPP (Rp)", f"{hpp:,.0f}")
    st.metric("Harga Jual (Rp)", f"{harga_jual:,.0f}")

    result = {
        "Tanggal": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Kemasan": selected_kemasan,
        "Harga Kemasan": harga_kemasan,
        "Biaya Gas": gas_harga,
        "Biaya Listrik": listrik_harga,
        "Biaya Air": air_harga,
        "Pajak (0.5%)": pajak,
        "HPP": hpp,
        "Harga Jual": harga_jual,
        "Margin (%)": margin
    }

    df = pd.DataFrame([result])

    if not os.path.exists("data_hpp.csv"):
        df.to_csv("data_hpp.csv", index=False)
    else:
        df.to_csv("data_hpp.csv", mode="a", index=False, header=False)

    st.subheader("📄 Tabel Ringkasan")
    st.dataframe(df.style.format("{:,.0f}", subset=["Harga Kemasan", "Biaya Gas", "Biaya Listrik", "Biaya Air", "Pajak (0.5%)", "HPP", "Harga Jual"]))

    st.download_button("📥 Unduh CSV", df.to_csv(index=False).encode("utf-8"), file_name="hasil_hpp.csv", mime="text/csv")

# ---------------- RESET ----------------
if st.button("🗑 Reset Semua Data"):
    if os.path.exists("data_hpp.csv"):
        os.remove("data_hpp.csv")
        st.warning("Data berhasil dihapus.")
