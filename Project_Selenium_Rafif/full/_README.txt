WHATSAPP BOT TDT - README

📌 DESKRIPSI
Bot WhatsApp otomatis berbasis Selenium yang dapat merespons pesan dari kontak tertentu (staff_contacts), membaca data dari file Excel dan TXT, serta mengirim pesan atau gambar secara otomatis. Bot ini dirancang untuk digunakan secara internal oleh tim TDT (contoh: Pak Rio, Rafif, Nayla).

⚙️ FITUR UTAMA
- Menampilkan waktu saat ini
- Cek stok barang dari file Stock.xlsx
- Tampilkan cuplikan Timeline.txt dan kirim gambar Timeline
- Cari deskripsi barang dari file data.xlsx
- Kirim gambar TDT berdasarkan nama file
- Log semua percakapan ke database SQLite dan file log harian (.txt)
- Deteksi otomatis saat tidak terkoneksi dengan WhatsApp Web, lalu reconnect
- Respon pesan diproses dengan multithreading untuk performa lebih cepat

🧠 CARA KERJA
1. Bot membuka WhatsApp Web dengan profil Chrome yang telah login.
2. Bot hanya merespons pesan dari daftar `staff_contacts`.
3. Bot akan memantau pesan masuk setiap 5 detik dan memprosesnya jika ada yang baru.
4. Pesan yang valid sesuai perintah (mulai, satu, dua, tiga, dst.) akan dijawab sesuai logika.
5. Semua interaksi disimpan dalam file log harian dan database SQLite.

📁 STRUKTUR FILE YANG DIBUTUHKAN
- `Stock.xlsx` : berisi data stok barang (Kolom B: Kode, Kolom C: Stok)
- `data.xlsx` : berisi data barang TDT (kolom pertama: kode TDT, kolom 2-27: detail)
- `Timeline.txt` : berisi cuplikan data timeline yang akan ditampilkan
- `logs/` : folder otomatis berisi log harian
- `CONFIG.py` : file Python berisi variabel CHROME_PROFILE_PATH (lokasi profil Chrome)

📂 LOKASI GAMBAR
- Folder gambar default: `HBSTDT-G`, bisa berisi file `.jpg` atau `.png`

🖥️ KONFIGURASI YANG HARUS DIPERIKSA
- CHROME_PROFILE_PATH : path ke profil Chrome yang sudah login ke WhatsApp Web
- driver_path : path ke chromedriver.exe yang sesuai dengan versi Google Chrome

🔄 MENJALANKAN BOT
Jalankan dari terminal/cmd:
    python nama_file_bot.py

✅ CATATAN
- Gunakan Selenium dengan versi chromedriver yang cocok dengan Chrome.
- Jangan jalankan lebih dari satu instance untuk menghindari bentrok kontrol UI.
- Jika WhatsApp Web logout, Anda harus login manual pada browser pertama kali.

© 2025 TDT Automation
