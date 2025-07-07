from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
from datetime import datetime

# 🎯 Nama kontak target
target_contact = "TDT Pak Rio"
rekap_file = "rekap_pesan_TDT_Pak_Rio.txt"

# 🛠️ Lokasi ChromeDriver
driver_path = r'C:\Users\Purchase (Arie)\Downloads\Laten\Selenium\chromedriver.exe'
service = Service(driver_path)
driver = webdriver.Chrome(service=service)

# 🌐 Akses WhatsApp Web
driver.get('https://web.whatsapp.com/')
print("🔄 Silakan scan QR code WhatsApp...")
WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.XPATH, '//div[@aria-label="Chat list"]')))

# 🔤 Fungsi pembersih karakter non-BMP agar tidak error
def clean_text(text):
    return ''.join(c for c in text if c <= '\uFFFF')

# 📩 Fungsi kirim pesan
def kirim_pesan(pesan):
    pesan = clean_text(pesan)
    try:
        input_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH,
                '//*[@id="main"]/footer/div[1]/div/span/div/div[2]/div/div[3]/div[1]/p'))
        )
        input_box.click()
        input_box.send_keys(pesan)
        input_box.send_keys(Keys.ENTER)
    except Exception as e:
        print(f"❗ Gagal mengirim pesan: {e}")

# 🔁 Variabel penyimpan pesan terakhir
last_message = ""

try:
    while True:
        sleep(5)
        chat_list = driver.find_elements(By.XPATH, '//div[@aria-label="Chat list"]//div[contains(@style,"z-index")]')
        found = False

        for chat in chat_list:
            try:
                name = chat.find_element(By.XPATH, './/span[@dir="auto"]').text
                if name == target_contact:
                    found = True
                    chat.click()
                    sleep(2)

                    # Ambil semua pesan masuk
                    messages = driver.find_elements(By.XPATH, '//div[contains(@class,"message-in")]//span[@dir="ltr"]')
                    if not messages:
                        continue

                    latest_message = messages[-1].text.strip().lower()

                    # Cek apakah pesan sudah dibalas sebelumnya
                    if latest_message != last_message:
                        last_message = latest_message
                        waktu = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                        # Simpan ke file rekap
                        with open(rekap_file, "a", encoding="utf-8") as f:
                            f.write(f"{waktu} | {target_contact}: {latest_message}\n")

                        # 💬 Respon berdasarkan isi pesan
                        if "mulai" in latest_message:
                            pesan = (
                                "Halo! Berikut pilihan yang tersedia:\n"
                                "👉 satu - Tampilkan jam saat ini\n"
                                "👉 dua - Sapa selamat pagi\n"
                                "👉 tiga - Perkiraan cuaca\n"
                                "👉 empat - Simpan pesan terakhir\n"
                                "👉 lima - Bebas interaksi\n"
                                "Ketik salah satu: satu, dua, tiga, empat, atau lima."
                            )
                            kirim_pesan(pesan)
                            print("📋 Menu dikirim.")

                        elif latest_message == "satu":
                            # Aksi: mengirim waktu saat ini
                            jam = datetime.now().strftime("%H:%M:%S")
                            kirim_pesan(f"⏰ Sekarang jam: {jam}")
                            print("🕒 Waktu dikirim.")

                        elif latest_message == "dua":
                            # Aksi: menyapa kontak
                            kirim_pesan(f"🌅 Selamat pagi, {target_contact}!")
                            print("🙋 Sapaan dikirim.")

                        elif latest_message == "tiga":
                            # Aksi: mengirim dummy cuaca
                            kirim_pesan("🌤️ Perkiraan cuaca hari ini: Cerah berawan, suhu sekitar 30°C.")
                            print("🌦️ Cuaca dikirim.")

                        elif latest_message == "empat":
                            # Aksi: menyimpan pesan ke file
                            kirim_pesan("📁 Pesan Anda sudah kami simpan ke rekap.")
                            print("📝 Pesan disimpan.")

                        elif latest_message == "lima":
                            # Aksi: bebas, respons fleksibel
                            kirim_pesan("😊 Apa yang bisa saya bantu hari ini?")
                            print("🤖 Respon fleksibel dikirim.")

                        else:
                            # Jika tidak sesuai opsi
                            kirim_pesan("❓ Mohon ketik mulai atau salah satu opsi (satu - lima).")
                            print("⚠️ Pesan tak dikenal.")
            except:
                continue

        if not found:
            print(f"⚠️ Kontak '{target_contact}' tidak ditemukan.")

except KeyboardInterrupt:
    print("⛔ Dihentikan oleh pengguna.")
    driver.quit()
