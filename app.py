import streamlit as st
import io
from fpdf import FPDF
import datetime

st.set_page_config(page_title="HPP Jasa Retort", layout="centered")
st.title("📦 Kalkulator HPP Jasa Retort UMKM")

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

jenis_kemasan = st.selectbox("Jenis Kemasan", ["Retort", "Standing Pouch"])
ukuran_kemasan = st.text_input("Ukuran Kemasan (ml)")
harga_kemasan = st.number_input("Harga Kemasan per pcs (Rp)", min_value=0)
jumlah_kemasan = st.number_input("Jumlah Produk Diproses", min_value=1, value=100)

st.subheader("🔌 Energi & Operasional")
biaya_listrik = st.number_input("Biaya Listrik (Rp)", min_value=0)
harga_gas_per_proses = st.number_input("Biaya Gas (Rp)", min_value=0)
harga_air_per_proses = st.number_input("Biaya Air (Rp)", min_value=0)
biaya_sewa_per_proses = st.number_input("Biaya Sewa Peralatan (Rp)", min_value=0)

# Hapus input margin keuntungan
# margin = st.slider("Margin Keuntungan (%)", min_value=10, max_value=100, value=30)

# Tambahkan input profit perusahaan
profit_persen = st.slider("Profit Perusahaan (%)", min_value=20, max_value=75, value=30)

# Hitung HPP
total_kemasan = harga_kemasan * jumlah_kemasan
total_operasional = biaya_listrik + harga_gas_per_proses + harga_air_per_proses + biaya_sewa_per_proses
biaya_total = total_kemasan + total_operasional
pajak = biaya_total * 0.005

# Perhitungan HPP tanpa margin, menggunakan profit perusahaan
harga_setelah_profit = biaya_total + pajak + (biaya_total * profit_persen / 100)
hpp_per_pcs = harga_setelah_profit / jumlah_kemasan

st.subheader("📊 Ringkasan")
st.write(f"Total Biaya: Rp {biaya_total:,.0f}")
st.write(f"Pajak 0.5%: Rp {pajak:,.0f}")
st.write(f"Profit {profit_persen}%: Rp {(biaya_total * profit_persen / 100):,.0f}")
st.write(f"Harga Setelah Profit: Rp {harga_setelah_profit:,.0f}")
st.success(f"HPP per pcs: Rp {hpp_per_pcs:,.0f}")

# Export PDF
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
    pdf.cell(200, 10, f"Total Biaya: Rp {biaya_total:,.0f}", ln=True)
    pdf.cell(200, 10, f"Pajak (0.5%): Rp {pajak:,.0f}", ln=True)
    pdf.cell(200, 10, f"Profit {profit_persen}%: Rp {(biaya_total * profit_persen / 100):,.0f}", ln=True)
    pdf.cell(200, 10, f"Harga Setelah Profit: Rp {harga_setelah_profit:,.0f}", ln=True)
    pdf.cell(200, 10, f"Harga Jual per pcs: Rp {hpp_per_pcs:,.0f}", ln=True)

    pdf_bytes = pdf.output(dest='S').encode('latin1')
    buffer = io.BytesIO(pdf_bytes)
    buffer.seek(0)

    st.download_button(
        label="📄 Download PDF",
        data=buffer,
        file_name=f"Laporan_HPP_{tanggal}.pdf",
        mime="application/pdf"
    )
