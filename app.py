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
# PERHITUNGAN FINAL (UPDATE)
# ----------------------------

# Komponen biaya
biaya_tenaga_kerja_harian = 150000
biaya_operasional = biaya_total * 0.30
biaya_cadangan_operasional = biaya_total * 0.10

# Total semua biaya
biaya_total_final = biaya_total + biaya_operasional + biaya_cadangan_operasional + biaya_tenaga_kerja_harian

# Pajak dan harga jual
pajak = biaya_total_final * 0.005
harga_setelah_pajak = biaya_total_final + pajak
harga_dengan_profit = harga_setelah_pajak * (1 + profit_persen / 100)

# Harga per pcs dan margin aktual
harga_jual_per_pcs = harga_dengan_profit / jumlah_kemasan
hpp_per_pcs = harga_setelah_pajak / jumlah_kemasan
laba_perusahaan = harga_dengan_profit - harga_setelah_pajak
margin_aktual = (harga_jual_per_pcs - hpp_per_pcs) / hpp_per_pcs * 100

# Target proses retort (jumlah pcs untuk menutup biaya)
target_mingguan_pcs = round(biaya_total_final / (harga_jual_per_pcs * 7))
target_bulanan_pcs = round(biaya_total_final / (harga_jual_per_pcs * 30))
target_3bulan_pcs = round(biaya_total_final / (harga_jual_per_pcs * 90))

# ----------------------------
# VISUALISASI
# ----------------------------
import matplotlib.pyplot as plt
import streamlit as st

st.markdown("### 🎯 Target Produksi (Jumlah pcs harus diretort)")
st.write(f"- **Target Mingguan**: {target_mingguan_pcs} pcs")
st.write(f"- **Target Bulanan**: {target_bulanan_pcs} pcs")
st.write(f"- **Target 3 Bulan**: {target_3bulan_pcs} pcs")

fig, ax = plt.subplots()
labels = ['1 Minggu', '1 Bulan', '3 Bulan']
values = [target_mingguan_pcs, target_bulanan_pcs, target_3bulan_pcs]
ax.bar(labels, values, color=['#4CAF50', '#FFC107', '#2196F3'])
ax.set_ylabel('Jumlah pcs')
ax.set_title('Target Produksi Harus Dicapai')
st.pyplot(fig)

# ----------------------------
# SARAN OTOMATIS
# ----------------------------
saran = ""
if margin_aktual < 10:
    saran = "⚠️ Margin terlalu rendah. Pertimbangkan menaikkan harga jual atau mengurangi biaya operasional."
elif target_bulanan_pcs > 1000:
    saran = "📊 Target bulanan cukup besar. Pastikan kapasitas produksi memadai dan tenaga kerja cukup."
else:
    saran = "✅ Struktur harga sudah optimal untuk mencapai profit."

st.markdown("### 💡 Saran Otomatis")
st.info(saran)

# ----------------------------
# EKSPOR CSV
# ----------------------------
import pandas as pd
if st.button("💾 Simpan CSV"):
    data = pd.DataFrame({
        "Ukuran Kemasan": [ukuran_kemasan],
        "Jumlah Kemasan": [jumlah_kemasan],
        "Biaya Total": [biaya_total],
        "Biaya Operasional": [biaya_operasional],
        "Cadangan Operasional": [biaya_cadangan_operasional],
        "Tenaga Kerja Harian": [biaya_tenaga_kerja_harian],
        "Total Biaya Final": [biaya_total_final],
        "Harga Jual per pcs": [harga_jual_per_pcs],
        "Margin Aktual": [f"{margin_aktual:.2f}%"],
        "Target Mingguan (pcs)": [target_mingguan_pcs],
        "Target Bulanan (pcs)": [target_bulanan_pcs],
        "Target 3 Bulan (pcs)": [target_3bulan_pcs],
        "Saran": [saran]
    })
    data.to_csv("perhitungan_hpp.csv", index=False)
    st.success("✅ Data berhasil disimpan dalam format CSV.")

# ----------------------------
# EKSPOR PDF
# ----------------------------
from fpdf import FPDF
import datetime

if st.button("🖨️ Ekspor PDF"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt="Laporan Perhitungan HPP", ln=True, align="C")
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Tanggal: {datetime.datetime.now().strftime('%d-%m-%Y')}", ln=True)

    pdf.ln(10)
    pdf.multi_cell(0, 10, txt=f"Ukuran Kemasan: {ukuran_kemasan}\n"
                               f"Jumlah Kemasan: {jumlah_kemasan}\n"
                               f"Biaya Total: Rp {biaya_total:,.0f}\n"
                               f"Biaya Operasional: Rp {biaya_operasional:,.0f}\n"
                               f"Cadangan Operasional: Rp {biaya_cadangan_operasional:,.0f}\n"
                               f"Tenaga Kerja Harian: Rp {biaya_tenaga_kerja_harian:,.0f}\n"
                               f"Total Biaya Final: Rp {biaya_total_final:,.0f}\n"
                               f"Harga Jual per pcs: Rp {harga_jual_per_pcs:,.0f}\n"
                               f"Margin Aktual: {margin_aktual:.2f}%\n"
                               f"Target Mingguan: {target_mingguan_pcs} pcs\n"
                               f"Target Bulanan: {target_bulanan_pcs} pcs\n"
                               f"Target 3 Bulan: {target_3bulan_pcs} pcs\n"
                               f"Saran: {saran}")

    pdf.output("laporan_hpp.pdf")
    st.success("✅ PDF berhasil diekspor.")


# ----------------------------
# RESET
# ----------------------------
if st.button("🔄 Reset"):
    for k in list(st.session_state.keys()):
        del st.session_state[k]
    st.rerun()
