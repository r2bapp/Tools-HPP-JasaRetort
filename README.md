### requirements.txt
streamlit
pandas
fpdf


### README.md
# HPP Retort Tools - Rumah Retort Bersama (R2B)

**HPP Jasa Kemasan dan Pengawetan dengan Retort** adalah aplikasi berbasis web (dibangun dengan Streamlit) untuk membantu pelaku usaha dalam menghitung harga pokok produksi (HPP) dan harga jual jasa retort berdasarkan biaya kemasan, energi, air, dan margin keuntungan.

---

## 🎯 Fitur Utama
- Login akses khusus (email whitelist)
- Pilih berbagai jenis kemasan retort & standing pouch
- Hitung biaya energi (gas, listrik), air, dan pajak otomatis
- Tentukan margin keuntungan sendiri
- Output HPP dan Harga Jual secara instan
- Simpan hasil ke CSV dan PDF
- Tab histori perhitungan & fitur reset data
- Desain UI clean, minimalis, dan edukatif dengan branding warna R2B (biru navy & kuning tua)

---

## 🚀 Cara Menjalankan (Local)
1. Clone repositori ini:
   ```bash
   git clone https://github.com/namakamu/hpp-retort-r2b.git
   cd hpp-retort-r2b
   ```
2. Install dependensi:
   ```bash
   pip install -r requirements.txt
   ```
3. Jalankan aplikasi:
   ```bash
   streamlit run app.py
   ```

---

## 🌐 Deploy ke Streamlit Cloud
1. Push project ini ke GitHub
2. Buka https://streamlit.io/cloud
3. Hubungkan ke repositori GitHub kamu
4. Jalankan `app.py` sebagai main file

---

## 📧 Akses Email yang Diizinkan
- rumahretortbersama1@gmail.com

---

## 📄 Lisensi
Proyek ini dikembangkan untuk kebutuhan internal dan edukasi pelaku UMKM di bawah Rumah Retort Bersama (R2B).
