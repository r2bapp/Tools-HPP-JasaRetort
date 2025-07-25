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

profit_persen = st.sidebar.slider("🧮 Target Profit Perusahaan (%)", min_value=1, max_value=150, value=15)

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

# Perhitungan harga pendapatan per proses (1 batch)
harga_per_proses = harga_jual_per_pcs * jumlah_kemasan

# Tambahkan margin 20% untuk menutup risiko & keuntungan
margin_safety = 1.2
target_pendapatan = biaya_total_final * margin_safety

# Hitung jumlah proses yang diperlukan per hari agar usaha bisa menutup semua biaya + margin
retort_per_hari = int(target_pendapatan / harga_per_proses)

# Jika ingin menetapkan default minimum 4 proses per hari (misalnya realistis dari kapasitas alat)
# Maka bisa gunakan: maksimal dari hasil perhitungan atau minimal 4
retort_per_hari = max(retort_per_hari, 4)

# Hitung untuk minggu/bulan
retort_per_minggu = retort_per_hari * 6     # 6 hari kerja
retort_per_bulan = retort_per_hari * 26     # 26 hari kerja rata-rata
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
# Aturan warna: jika target harian terlalu tinggi, beri warna merah
if retort_per_hari <= 4:
    warna = "green"
    keterangan = "Target realistis 👍"
else:
    warna = "red"
    keterangan = "Target terlalu tinggi ⚠️"

# Tampilkan target per hari dengan warna
st.markdown(f"<span style='color:{warna}; font-size:18px;'>🔸 Per Hari: <b>{retort_per_hari}</b> proses – {keterangan}</span>", unsafe_allow_html=True)

# Sisanya bisa tetap standar
st.write(f"- Per Minggu: {retort_per_minggu} proses")
st.write(f"- Per Bulan: {retort_per_bulan} proses")
st.write(f"- Per 3 Bulan: {retort_per_3bulan} proses")

st.markdown("### 📍 Profitabilitas")
st.write(f"- 💵 Profit Kotor: Rp {profit_kotor:,.0f}")
st.write(f"- 💼 Profit Bersih: Rp {profit_bersih:,.0f}")

# Insight Otomatis
st.markdown("### 🤖 Insight Otomatis Berbasis Data")

# 1. Margin lebih kecil dari target
if margin_aktual < profit_persen:
    st.warning("⚠️ Margin lebih kecil dari target profit. Pertimbangkan untuk menaikkan harga jual atau menurunkan biaya produksi.")

# 2. Biaya operasional terlalu tinggi (lebih dari 35% dari total biaya)
if biaya_operasional > biaya_total * 0.35:
    st.warning("⚠️ Biaya operasional melebihi 35% dari total biaya. Evaluasi penggunaan listrik, gas, dan air untuk efisiensi.")

# 3. Harga jual per pcs tinggi → Validasi dengan pasar
if harga_jual_per_pcs > 10000:
    st.info("💡 Harga jual per pcs cukup tinggi. Pastikan segmen pasar mampu menerima harga ini.")

# 4. Semua aman → indikator sehat
if (
    margin_aktual >= profit_persen and
    biaya_operasional <= biaya_total * 0.35 and
    harga_jual_per_pcs <= 10000
):
    st.success("✅ Biaya dan margin terlihat sehat untuk model bisnis saat ini.")

# Perbandingan Margin Aktual vs Ideal
st.markdown("### 📊 Perbandingan Margin Aktual vs Target")

# Hitung selisih margin
selisih_margin = margin_aktual - profit_persen
selisih_persen = (selisih_margin / profit_persen) * 100 if profit_persen != 0 else 0

# Tampilkan nilai margin
st.write(f"- Target Margin: {profit_persen:.2f}%")
st.write(f"- Margin Aktual: {margin_aktual:.2f}%")

# Interpretasi visual
if selisih_margin >= 0:
    st.success(f"✅ Margin aktual lebih tinggi dari target sebesar {selisih_persen:.2f}%")
else:
    st.error(f"❌ Margin aktual lebih rendah dari target sebesar {abs(selisih_persen):.2f}%")

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
# EKSPOR CSV
# ----------------------------
if st.button("💾 Simpan CSV"):
    data = pd.DataFrame({
        "Jenis Kemasan": [jenis_kemasan],
        "Ukuran Kemasan": [ukuran_kemasan],
        "Harga Kemasan": [harga_kemasan],
        "Jumlah Produk": [jumlah_kemasan],
        "Total Biaya": [biaya_total],
        "Biaya Operasional": [biaya_operasional],
        "Biaya Tenaga Kerja": [biaya_tenaga_kerja],
        "Cadangan": [cadangan_operasional],
        "Pajak": [pajak],
        "Total Setelah Pajak": [biaya_setelah_pajak],
        "HPP per pcs": [hpp_per_pcs],
        "Harga Jual per pcs": [harga_jual_per_pcs],
        "Laba Perusahaan": [laba_perusahaan],
        "Margin (%)": [margin_aktual]
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
    pdf.set_text_color(0, 31, 63)
    pdf.cell(200, 10, "Laporan HPP Jasa Retort", ln=True, align='C')

    pdf.set_font("Arial", '', 12)
    pdf.set_text_color(0, 0, 0)
    pdf.ln(10)
    tanggal = datetime.datetime.now().strftime('%d-%m-%Y %H:%M')
    pdf.cell(200, 10, f"Tanggal Input: {tanggal}", ln=True)
    pdf.cell(200, 10, f"Jenis Kemasan: {jenis_kemasan}", ln=True)
    pdf.cell(200, 10, f"Ukuran Kemasan: {ukuran_kemasan}", ln=True)
    pdf.cell(200, 10, f"Harga Kemasan per pcs: Rp {harga_kemasan:,}", ln=True)
    pdf.cell(200, 10, f"Jumlah Produk Diproses: {jumlah_kemasan} pcs", ln=True)
    pdf.cell(200, 10, f"Biaya Listrik: Rp {biaya_listrik:,.0f}", ln=True)
    pdf.cell(200, 10, f"Biaya Gas: Rp {harga_gas_per_proses:,.0f}", ln=True)
    pdf.cell(200, 10, f"Biaya Air: Rp {harga_air_per_proses:,.0f}", ln=True)
    pdf.cell(200, 10, f"Biaya Sewa: Rp {biaya_sewa_per_proses:,.0f}", ln=True)
    pdf.cell(200, 10, f"Total Biaya Produksi: Rp {biaya_total:,.0f}", ln=True)
    pdf.cell(200, 10, f"Biaya Operasional: Rp {biaya_operasional:,.0f}", ln=True)
    pdf.cell(200, 10, f"Cadangan Operasional: Rp {cadangan_operasional:,.0f}", ln=True)
    pdf.cell(200, 10, f"Biaya Tenaga Kerja: Rp {biaya_tenaga_kerja:,.0f}", ln=True)
    pdf.cell(200, 10, f"Pajak (0.5%): Rp {pajak:,.0f}", ln=True)
    pdf.cell(200, 10, f"Total Setelah Pajak: Rp {biaya_setelah_pajak:,.0f}", ln=True)
    pdf.cell(200, 10, f"Laba Perusahaan ({profit_persen}%): Rp {laba_perusahaan:,.0f}", ln=True)
    pdf.cell(200, 10, f"Harga Jual Total: Rp {harga_jual_total:,.0f}", ln=True)
    pdf.cell(200, 10, f"Harga Jual per pcs: Rp {harga_jual_per_pcs:,.0f}", ln=True)
    pdf.cell(200, 10, f"Margin Aktual: {margin_aktual:.2f}%", ln=True)

    buffer = io.BytesIO()
    pdf.output(buffer)
    buffer.seek(0)

    st.download_button(
        label="📄 Download PDF",
        data=buffer,
        file_name=f"Laporan_HPP_{tanggal}.pdf",
        mime="application/pdf"
    )

# ----------------------------
# RESET
# ----------------------------
if st.button("🔄 Reset"):
    for k in list(st.session_state.keys()):
        del st.session_state[k]
    st.rerun()
