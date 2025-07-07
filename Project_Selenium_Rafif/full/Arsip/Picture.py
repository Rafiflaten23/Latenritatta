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
from CONFIG import CHROME_PROFILE_PATH
import pyautogui

# CONFIG #
staff_contacts = ["TDT Pak Rio Rio", "rafif"]
driver_path = r'C:\Users\Purchase (Arie)\Dropbox\SHERING PK ADRIAN\py_SeleniumTesting\full\chromedriver.exe'
connection_check_interval = 5  # detik
log_folder = "logs"
os.makedirs(log_folder, exist_ok=True)

def get_log_filename():
    return os.path.join(log_folder, f"log_{datetime.now().strftime('%Y-%m-%d')}.txt")


def clean_text(text):
    return ''.join(c for c in text if c <= '\uFFFF')


def send_multiline_message(input_box, message):
    lines = message.split('\n')
    for i, line in enumerate(lines):
        input_box.send_keys(line)
        if i != len(lines) - 1:
            input_box.send_keys(Keys.SHIFT, Keys.ENTER)
    input_box.send_keys(Keys.ENTER)


class WhatsAppBot:
    def __init__(self):
        self.driver = None
        self.conn = sqlite3.connect("whatsapp_logs.db")
        self.cursor = self.conn.cursor()
        self.last_messages = {}
        self.was_disconnected = False
        self.user_states = {}

    def initialize_driver(self):
        options = webdriver.ChromeOptions()
        options.add_argument(f"user-data-dir={CHROME_PROFILE_PATH}")
        service = Service(driver_path)
        self.driver = webdriver.Chrome(service=service, options=options)

    def connect(self):
        print("\U0001F504 Connecting to WhatsApp Web...")
        if not self.driver:
            self.initialize_driver()
        self.driver.get("https://web.whatsapp.com/")
        try:
            WebDriverWait(self.driver, 60).until(
                EC.presence_of_element_located((By.XPATH, '//div[@aria-label="Chat list"]'))
            )
            print("\u2705 Connected to WhatsApp Web")
            return True
        except:
            print("\u274C Failed to connect")
            return False

    def check_connection(self):
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//div[@aria-label="Chat list"]'))
            )
            return True
        except:
            return False

    def check_no_connection(self):
        try:
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((
                    By.XPATH,
                    '//*[@id="side"]/span[1]/div/div/div[2]/div[1] | //*[@id="side"]/span/div/div[2]/div[1]/div'
                ))
            )
            return True
        except:
            return False

    def create_table_if_not_exists(self, year):
        table_name = f"log_{year}"
        self.cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                waktu TEXT,
                kontak TEXT,
                pesan TEXT
            )
        """)
        self.conn.commit()

    def find_and_select_contact(self, contact_name):
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//div[@aria-label="Chat list"]'))
            )
            chat_list = self.driver.find_elements(By.XPATH, '//div[@aria-label="Chat list"]//div[contains(@style,"z-index")]')
            for chat in chat_list:
                try:
                    name_element = chat.find_element(By.XPATH, './/span[@dir="auto"]')
                    if name_element.text.strip().lower() == contact_name.lower():
                        chat.click()
                        sleep(2)
                        return True
                except:
                    continue
            print(f"\u26A0\uFE0F Contact '{contact_name}' not found.")
            return False
        except Exception as e:
            print(f"\u274C Error finding contact: {e}")
            return False

    def get_chat_name(self):
        try:
            name_element = self.driver.find_element(By.XPATH, '//header//span[@dir="auto"]')
            return name_element.text.strip()
        except:
            return "Unknown"

    def reply_and_log(self, contact_name, latest_message, response_text):
        waktu = datetime.now()
        year = waktu.year
        self.create_table_if_not_exists(year)

        log_line = f"{waktu.strftime('%Y-%m-%d %H:%M:%S')} | {contact_name}: {latest_message}\n"
        with open(get_log_filename(), "a", encoding="utf-8") as f:
            f.write(log_line)

        self.cursor.execute(
            f"INSERT INTO log_{year} (waktu, kontak, pesan) VALUES (?, ?, ?)",
            (waktu.strftime("%Y-%m-%d %H:%M:%S"), contact_name, latest_message)
        )
        self.conn.commit()

        try:
            input_box = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div[contenteditable="true"][data-tab="10"]'))
            )
            input_box.click()
            response_text = clean_text(response_text)
            send_multiline_message(input_box, response_text)
        except Exception as e:
            print(f"\u274C Gagal membalas pesan: {e}")

        print(f"\u2705 Pesan dari {contact_name} dibalas dan dicatat.")

    def send_image(self, contact_name, image_name):
        # Path ke folder gambar
        image_folder = r'C:\Users\Purchase (Arie)\Dropbox\A1.CATALOG TDT\HBSTDT-G'
        image_path_jpg = os.path.join(image_folder, f"{image_name}.jpg")
        image_path_png = os.path.join(image_folder, f"{image_name}.png")

        if not self.find_and_select_contact(contact_name):
            print(f"❌ Gagal menemukan kontak: {contact_name}")
            return

        try:
            # Klik tombol attach
            attach_btn = WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="main"]/footer/div[1]/div/span/div/div[1]/div/button/span'))
            )
            attach_btn.click()
            sleep(1)

            # Klik submenu Photo and Video
            photo_video_btn = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div/span[5]/div/ul/div/div/div[2]/li'))
            )
            photo_video_btn.click()
            sleep(1)

            # Pilih gambar yang sesuai
            if os.path.exists(image_path_jpg):
                file_input = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//input[@type="file"]'))
                )
                file_input.send_keys(image_path_jpg)
                sleep(2)

                # Klik tombol kirim
                send_btn = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, '//span[@data-icon="send"]'))
                )
                send_btn.click()

                print(f"✅ Gambar {image_name}.jpg berhasil dikirim ke {contact_name}")
            elif os.path.exists(image_path_png):
                file_input = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//input[@type="file"]'))
                )
                file_input.send_keys(image_path_png)
                sleep(2)

                # Klik tombol kirim
                send_btn = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, '//span[@data-icon="send"]'))
                )
                send_btn.click()

                print(f"✅ Gambar {image_name}.png berhasil dikirim ke {contact_name}")
            else:
                print(f"⚠️ Gambar {image_name} tidak ditemukan di folder.")

        except Exception as e:
            print(f"❌ Gagal kirim gambar ke {contact_name}: {e}")

    def monitor_messages(self):
        try:
            while True:
                if self.check_no_connection():
                    print("\u274C Tidak ada koneksi...")
                    self.was_disconnected = True
                    sleep(connection_check_interval)
                    continue

                if self.check_connection() and self.was_disconnected:
                    print("\U0001F501 Reconnected! Sending status message.")
                    self.was_disconnected = False
                    for contact in staff_contacts:
                        self.send_status_message(contact)

                chats = self.driver.find_elements(By.XPATH, '//div[@aria-label="Chat list"]//div[contains(@style,"z-index")]')
                for chat in chats:
                    try:
                        chat.click()
                        sleep(1)

                        contact_name = self.get_chat_name()
                        messages = self.driver.find_elements(By.XPATH, '//div[contains(@class,"message-in")]//span[@dir="ltr"]')
                        if not messages:
                            continue
                        latest_message = messages[-1].text.strip()

                        last_msg = self.last_messages.get(contact_name)
                        if latest_message != last_msg:
                            self.last_messages[contact_name] = latest_message

                            if contact_name in staff_contacts:
                                self.handle_command(contact_name, latest_message.lower())
                            else:
                                self.reply_and_log(contact_name, latest_message, "Access Denied")
                        else:
                            print(f"\U0001F501 Pesan dari {contact_name} sudah dicatat sebelumnya.")
                    except Exception as e:
                        print(f"\u26A0\uFE0F Error saat memproses chat: {e}")
                        continue

                sleep(connection_check_interval)

        except KeyboardInterrupt:
            print("\u26D4 Dihentikan oleh pengguna.")
        except Exception as e:
            print(f"\u2757 Error: {e}")
        finally:
            if self.driver:
                self.driver.quit()
            if self.conn:
                self.conn.close()

    def handle_command(self, contact_name, message):
        state = self.user_states.get(contact_name, "main_menu")
        message = message.strip().lower()

        if state == "main_menu":
            if message == "mulai":
                response = (
                    "Selamat datang di layanan otomatis kami!\n\n"
                    "Berikut adalah beberapa pilihan menu yang dapat Anda gunakan:\n"
                    "satu   : Tampilkan jam saat ini\n"
                    "dua    : Sapaan selamat pagi\n"
                    "tiga   : Perkiraan cuaca hari ini\n"
                    "empat  : Simpan pesan terakhir\n"
                    "lima   : Kirim gambar/video\n\n"
                    "Silakan ketik salah satu opsi di atas untuk melanjutkan."
                )
                self.user_states[contact_name] = "waiting_choice"
            else:
                response = "⚠️ Mohon ketik 'mulai' untuk memulai menu layanan kami :)."

        elif state == "waiting_choice":
            if message == "satu":
                response = f"⏰ Saat ini waktu menunjukkan pukul: {datetime.now().strftime('%H:%M:%S')}\n\nSilakan pilih menu lainnya:\n👉 satu\n👉 dua\n👉 tiga\n👉 empat\n👉 lima"
            elif message == "dua":
                response = f"🌞 Selamat pagi, {contact_name}! Semoga hari Anda menyenangkan.\n\nSilakan pilih menu lainnya:\n👉 satu\n👉 dua\n👉 tiga\n👉 empat\n👉 lima"
            elif message == "tiga":
                response = "🌦️ Cuaca hari ini cerah! Suhu sekitar 28°C.\n\nSilakan pilih menu lainnya:\n👉 satu\n👉 dua\n👉 tiga\n👉 empat\n👉 lima"
            elif message == "empat":
                response = "Pesan terakhir sudah disimpan!\n\nSilakan pilih menu lainnya:\n👉 satu\n👉 dua\n👉 tiga\n👉 empat\n👉 lima"
            elif message == "lima":
                response = "💡 Silakan kirimkan nama gambar/video yang ingin Anda terima."
                self.user_states[contact_name] = "waiting_image_name"
            else:
                response = "⚠️ Pilihan tidak valid. Ketik 'mulai' untuk memulai menu layanan."

        elif state == "waiting_image_name":
            image_name = message.strip()
            self.send_image(contact_name, image_name)

            response = f"📷 Gambar {image_name} telah dikirim!"
            self.user_states[contact_name] = "main_menu"

        self.reply_and_log(contact_name, message, response)


if __name__ == "__main__":
    bot = WhatsAppBot()
    if bot.connect():
        bot.monitor_messages()
