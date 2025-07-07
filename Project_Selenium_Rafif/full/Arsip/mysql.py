def mysql_connection():
    print("Menghubungkan ke MySQL")
    # Tambahkan kode asli dari mysql.py di sini

import os
import sqlite3
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
from datetime import datetime

# Nama kontak target
target_contact = "TDT Pak Rio"

# Path ke ChromeDriver
driver_path = r'C:\Users\Purchase (Arie)\Downloads\Laten\Selenium\chromedriver.exe'
service = Service(driver_path)
driver = webdriver.Chrome(service=service)

# Koneksi ke database SQLite
conn = sqlite3.connect("whatsapp_logs.db")
cursor = conn.cursor()

# Fungsi buat tabel per tahun kalau belum ada
def create_table_if_not_exists(year):
    table_name = f"log_{year}"
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            waktu TEXT,
            kontak TEXT,
            pesan TEXT
        )
    """)
    conn.commit()

# Fungsi untuk ambil pesan terakhir yang sudah dicatat
def load_last_message():
    try:
        with open("last_message.txt", "r", encoding="utf-8") as f:
            return f.read().strip()
    except:
        return ""

# Fungsi untuk simpan pesan terakhir
def save_last_message(message):
    with open("last_message.txt", "w", encoding="utf-8") as f:
        f.write(message)

last_message = load_last_message()

# Buka WhatsApp Web
driver.get('https://web.whatsapp.com/')
print("🔄 Silakan scan QR code WhatsApp...")

# Tunggu sampai chat list muncul
WebDriverWait(driver, 60).until(
    EC.presence_of_element_located((By.XPATH, '//div[@aria-label="Chat list"]'))
)

try:
    while True:
        sleep(5)  # jeda agar tidak terlalu cepat

        # Ambil semua chat di daftar
        chat_list = driver.find_elements(By.XPATH, '//div[@aria-label="Chat list"]//div[contains(@style,"z-index")]')

        found_target = False

        for chat in chat_list:
            try:
                name_element = chat.find_element(By.XPATH, './/span[@dir="auto"]')
                contact_name = name_element.text

                if contact_name == target_contact:
                    found_target = True
                    chat.click()
                    sleep(2)

                    # Ambil pesan terakhir
                    messages = driver.find_elements(By.XPATH, '//div[contains(@class,"message-in")]//span[@dir="ltr"]')
                    if messages:
                        latest_message = messages[-1].text.strip()
                    else:
                        latest_message = ""

                    if latest_message and latest_message != last_message:
                        last_message = latest_message
                        save_last_message(latest_message)

                        waktu = datetime.now()
                        year = waktu.year
                        create_table_if_not_exists(year)

                        # Simpan ke database SQLite
                        cursor.execute(
                            f"INSERT INTO log_{year} (waktu, kontak, pesan) VALUES (?, ?, ?)",
                            (waktu.strftime("%Y-%m-%d %H:%M:%S"), target_contact, latest_message)
                        )
                        conn.commit()

                        # Kirim balasan otomatis
                        input_box = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, 'div[contenteditable="true"][data-tab="10"]'))
                        )
                        input_box.click()
                        input_box.send_keys("Selamat Datang")
                        input_box.send_keys(Keys.ENTER)

                        print(f"✅ Pesan baru dari {target_contact} dibalas dan disimpan.")
                    else:
                        print("🔁 Tidak ada pesan baru.")
                    break

            except Exception as e:
                print(f"❗ Gagal membaca chat: {e}")
                continue

        if not found_target:
            print(f"⚠️ Kontak '{target_contact}' tidak ditemukan di chat list.")

except KeyboardInterrupt:
    print("⛔ Dihentikan oleh pengguna.")
    conn.close()
    driver.quit()

except Exception as e:
    print(f"❗ Error: {e}")
    conn.close()
    driver.quit()
