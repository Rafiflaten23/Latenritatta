import os
import sqlite3
import pyautogui
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
from datetime import datetime
from CONFIG import CHROME_PROFILE_PATH

# CONFIG #
staff_contacts = ["TDT Pak Rio Rio", "rafif","HP Kantor"]
driver_path = r'C:\Users\Mipan\Dropbox\3.Kerjaan\1.PUTRAJAYA PROTOCORP\FOLDER RAFIF (PURCHASE)\py_SeleniumTesting\full\chromedriver.exe'
image_folder = r'C:\Users\Mipan\Dropbox\3.Kerjaan\1.PUTRAJAYA PROTOCORP\A1.CATALOG TDT\HBSTDT-G'
timeline_excel_path = 'Timeline.txt'
connection_check_interval = 5
log_folder = "logs"
os.makedirs(log_folder, exist_ok=True)
excel_path = 'data.xlsx'

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

    def check_stock(self, kode_barang):
        try:
            df = pd.read_excel("Stock.xlsx", engine="openpyxl", usecols="B:C")
            df.columns = ["Kode", "Stok"]

            match = df[df["Kode"].astype(str).str.lower() == kode_barang.lower()]
            if match.empty:
                return "❌ Kode barang tidak ada atau stok kosong."

            stok = match.iloc[0]["Stok"]
            stok = 0 if pd.isna(stok) else int(stok)
            if stok == 0:
                return f"📦 Kode: {kode_barang.upper()} — Stok: 0 (Kosong)"
            else:
                return f"📦 Kode: {kode_barang.upper()} — Stok tersedia: {stok}"
        except Exception as e:
            return f"❌ Gagal membaca file Stock.xlsx:\n{str(e)}"
    
    def initialize_driver(self):
        options = webdriver.ChromeOptions()
        options.add_argument(f"user-data-dir={CHROME_PROFILE_PATH}")
        service = Service(driver_path)
        self.driver = webdriver.Chrome(service=service, options=options)

    def connect(self):
        print("🔄 Connecting to WhatsApp Web...")
        if not self.driver:
            self.initialize_driver()
        self.driver.get("https://web.whatsapp.com/")
        try:
            WebDriverWait(self.driver, 60).until(
                EC.presence_of_element_located((By.XPATH, '//div[@aria-label="Chat list"]'))
            )
            print("✅ Connected to WhatsApp Web")
            return True
        except:
            print("❌ Failed to connect")
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
                EC.presence_of_element_located((By.XPATH,
                    '//*[@id="side"]/span[1]/div/div/div[2]/div[1] | //*[@id="side"]/span/div/div[2]/div[1]/div'))
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
            print(f"⚠️ Contact '{contact_name}' not found.")
            return False
        except Exception as e:
            print(f"❌ Error finding contact: {e}")
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
            send_multiline_message(input_box, clean_text(response_text))
        except Exception as e:
            print(f"❌ Gagal membalas pesan: {e}")

        print(f"✅ Pesan dari {contact_name} dibalas dan dicatat.")

    def send_image(self, contact_name, image_name):
        image_path_jpg = os.path.join(image_folder, image_name + ".jpg")
        image_path_png = os.path.join(image_folder, image_name + ".png")
        image_path = image_path_jpg if os.path.exists(image_path_jpg) else image_path_png if os.path.exists(image_path_png) else None

        if not image_path:
            print("❌ Gambar tidak ditemukan.")
            self.reply_and_log(contact_name, image_name, "❌ File tidak ditemukan. Pastikan nama file benar.")
            return

        try:
            if not self.find_and_select_contact(contact_name):
                return

            attach_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="main"]/footer/div[1]/div/span/div/div[1]/div/button/span'))
            )
            attach_button.click()
            sleep(1)

            photo_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div/span[6]/div/ul/div/div/div[2]/li'))
            )
            photo_button.click()
            sleep(1)

            file_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//input[@accept="image/*,video/mp4,video/3gpp,video/quicktime"]'))
            )
            file_input.send_keys(image_path)
            sleep(2)

            send_btn = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//span[@data-icon="send"]'))
            )
            send_btn.click()
            sleep(1)
            pyautogui.press('esc')
            print(f"📤 Gambar '{os.path.basename(image_path)}' dikirim ke {contact_name}.")
        except Exception as e:
            print(f"❌ Gagal kirim gambar: {e}")

    def lookup_tdt_description(self, kode_tdt):
        try:
            df = pd.read_excel(excel_path, engine='openpyxl')
            row = df[df.iloc[:, 0].astype(str).str.lower() == kode_tdt.lower()]
            if row.empty:
                return "❌ Kode TDT tidak ditemukan."

            details = row.iloc[0, 1:27]
            result = "\n".join([f"{df.columns[i]}: {details[i-1]}" for i in range(1, 27)])
            return f"📄 Hasil pencarian untuk '{kode_tdt}':\n\n{result}"
        except Exception as e:
            return f"❌ Terjadi kesalahan saat membaca file Excel:\n{str(e)}"

    def get_timeline_preview(self):
        try:
            with open(timeline_excel_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            preview_lines = lines[:32]  # Ambil 10 baris pertama
            if not preview_lines:
                return "❌ File Timeline.txt kosong."
            
            result = "".join(preview_lines)
            return f"📋 Cuplikan data dari Timeline.txt:\n\n{result}"
        except Exception as e:
            return f"❌ Gagal membaca Timeline.txt:\n{str(e)}"


    def handle_command(self, contact_name, message):
        state = self.user_states.get(contact_name, "main_menu")
        message = message.strip()

        if state == "main_menu":
            if message.lower() == "mulai":
                response = (
                    "Selamat datang di layanan otomatis kami!\n\n"
                    "Berikut adalah beberapa pilihan menu:\n"
                    "satu   : Tampilkan jam saat ini\n"
                    "dua    : Cek Stock TDT\n"
                    "tiga   : Timeline TDT\n"
                    "empat  : Cari barang TDT\n"
                    "lima   : Mencari gambar TDT\n\n"
                    "Silakan ketik salah satu opsi di atas."
                )
                self.user_states[contact_name] = "waiting_choice"
            else:
                response = "⚠️ Mohon ketik 'mulai' untuk memulai menu layanan TDT."

        elif state == "waiting_choice":
            if message.lower() == "satu":
                response = f"⏰ Waktu saat ini: {datetime.now().strftime('%H:%M:%S')}"

            elif message.lower() == "dua":
                response = "📥 Silakan ketik kode barang yang ingin dicek stok-nya (contoh: TDT123)"
                self.user_states[contact_name] = "waiting_stock_code"
                self.reply_and_log(contact_name, message, response)
                return

            elif message.lower() == "tiga":
                preview = self.get_timeline_preview()
                self.reply_and_log(contact_name, message, preview)
                self.send_image(contact_name, "Timeline")
                return
            elif message.lower() == "empat":
                response = "📥 Silakan ketik kode TDT yang ingin dicari (contoh: TDT001)"
                self.user_states[contact_name] = "waiting_tdt_code"
                self.reply_and_log(contact_name, message, response)
                return
            elif message.lower() == "lima":
                response = "🖼️ Silakan ketik nama gambar (tanpa ekstensi .jpg/.png)."
                self.user_states[contact_name] = "waiting_image_name"
                self.reply_and_log(contact_name, message, response)
                return
            else:
                response = "❌ Pilihan tidak dikenal. Ketik salah satu: satu, dua, tiga, empat, lima."
            self.user_states[contact_name] = "waiting_choice"

        elif state == "waiting_image_name":
            self.send_image(contact_name, message)
            self.user_states[contact_name] = "waiting_choice"
            return

        elif state == "waiting_tdt_code":
            result = self.lookup_tdt_description(message)
            self.reply_and_log(contact_name, message, result)
            self.user_states[contact_name] = "waiting_choice"
            return
        
        elif state == "waiting_stock_code":
            result = self.check_stock(message)
            self.reply_and_log(contact_name, message, result)
            self.user_states[contact_name] = "waiting_choice"
            return

        else:
            response = "⚠️ Sistem error. Ketik 'mulai' untuk memulai ulang."

        self.reply_and_log(contact_name, message, response)

    def send_status_message(self, contact_name):
        if not self.find_and_select_contact(contact_name):
            return
        try:
            input_box = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div[contenteditable="true"][data-tab="10"]'))
            )
            input_box.click()
            input_box.send_keys("Selenium Online")
            input_box.send_keys(Keys.ENTER)
        except Exception as e:
            print(f"❌ Gagal kirim status: {e}")

    def monitor_messages(self):
        try:
            while True:
                if self.check_no_connection():
                    print("❌ Tidak ada koneksi...")
                    self.was_disconnected = True
                    sleep(connection_check_interval)
                    continue

                if self.check_connection() and self.was_disconnected:
                    print("🔁 Reconnected.")
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

                        if latest_message != self.last_messages.get(contact_name):
                            self.last_messages[contact_name] = latest_message
                            if contact_name in staff_contacts:
                                self.handle_command(contact_name, latest_message)
                            else:
                                self.reply_and_log(contact_name, latest_message, "Access Denied")
                    except Exception as e:
                        print(f"⚠️ Error saat memproses chat: {e}")
                        continue

                sleep(connection_check_interval)

        except KeyboardInterrupt:
            print("⛔ Dihentikan oleh pengguna.")
        finally:
            if self.driver:
                self.driver.quit()
            if self.conn:
                self.conn.close()

    def run(self):
        print("🚀 Starting WhatsApp Bot...")
        while True:
            if not self.check_connection():
                if not self.connect():
                    print(f"🔁 Reconnecting in {connection_check_interval} seconds...")
                    sleep(connection_check_interval)
                    continue
            self.monitor_messages()

if __name__ == "__main__":
    bot = WhatsAppBot()
    bot.run()
