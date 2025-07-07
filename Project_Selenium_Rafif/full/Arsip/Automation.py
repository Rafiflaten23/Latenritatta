from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
from datetime import datetime

# Nama kontak yang ingin dipantau
target_contact = "TDT Pak Rio"

# Path ke ChromeDriver
driver_path = r'C:\Users\Purchase (Arie)\Downloads\Laten\Selenium\chromedriver.exe'
service = Service(driver_path)
driver = webdriver.Chrome(service=service)

# Buka WhatsApp Web
driver.get('https://web.whatsapp.com/')
print("🔄 Silakan scan QR code WhatsApp...")

# Tunggu sampai chat list muncul
WebDriverWait(driver, 60).until(
    EC.presence_of_element_located((By.XPATH, '//div[@aria-label="Chat list"]'))
)

# Simpan pesan terakhir untuk deteksi perubahan
last_message = ""
rekap_file = "rekap_pesan_TDT_Pak_Rio.txt"

try:
    while True:
        sleep(5)  # jeda agar tidak terlalu cepat

        # Ambil semua elemen nama kontak di daftar chat
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

                    # Ambil pesan terakhir dari kontak
                    messages = driver.find_elements(By.XPATH, '//div[contains(@class,"message-in")]//span[@dir="ltr"]')
                    if messages:
                        latest_message = messages[-1].text.strip()
                    else:
                        latest_message = ""

                    if latest_message and latest_message != last_message:
                        last_message = latest_message

                        waktu = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        with open(rekap_file, "a", encoding="utf-8") as f:
                            f.write(f"{waktu} | {target_contact}: {latest_message}\n")

                        # Balas pesan
                        input_box = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, 'div[contenteditable="true"][data-tab="10"]'))
                        )
                        input_box.click()
                        input_box.send_keys("Selamat Datang")
                        input_box.send_keys(Keys.ENTER)

                        print(f"✅ Pesan dari {target_contact} dibalas dan direkap.")
                    else:
                        print("🔁 Tidak ada pesan baru.")
                    break  # keluar dari for loop karena sudah ketemu target

            except Exception as e:
                continue

        if not found_target:
            print(f"⚠️ Kontak '{target_contact}' tidak ditemukan di chat list.")

except KeyboardInterrupt:
    print("⛔ Dihentikan oleh pengguna.")
    driver.quit()

except Exception as e:
    print(f"❗ Error: {e}")
    driver.quit()
