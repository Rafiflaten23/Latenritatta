from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
from datetime import datetime
from CONFIG import CHROME_PROFILE_PATH

# Configuration
target_contact = "Test number"
driver_path = r'C:\Users\Purchase (Arie)\Dropbox\SHERING PK ADRIAN\py_SeleniumTesting\full\chromedriver.exe'
rekap_file = "rekap_pesan_TDT_Pak_Rio.txt"
test_message = "Selenium Online"
connection_check_interval = 5  # seconds

class WhatsAppBot:
    def __init__(self):
        self.driver = None
        self.last_message = ""
        self.is_first_connection = True
        self.was_disconnected = False  # New flag to track disconnection

    def initialize_driver(self):
        options = webdriver.ChromeOptions()
        options.add_argument(f"user-data-dir={CHROME_PROFILE_PATH}")
        service = Service(driver_path)
        self.driver = webdriver.Chrome(service=service, options=options)
        return self.driver

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
                    # Gabungan XPath WA dan WA Business
                    '//*[@id="side"]/span[1]/div/div/div[2]/div[1] | //*[@id="side"]/span/div/div[2]/div[1]/div'
                ))
            )
            print("❌ Komputer tidak terkoneksi ke WhatsApp Web (Business/Biasa)")
            return True
        except:
            return False

    def connect(self):
        print("🔄 Connecting to WhatsApp Web...")
        if not self.driver:
            self.initialize_driver()

        self.driver.get("https://web.whatsapp.com/")

        try:
            WebDriverWait(self.driver, 60).until(
                EC.presence_of_element_located((By.XPATH, '//div[@aria-label="Chat list"]'))
            )
            print("✅ Successfully connected to WhatsApp Web")

            if self.is_first_connection:
                self.send_test_message()
                self.is_first_connection = False

            return True
        except:
            print("❌ Failed to connect to WhatsApp Web")
            return False

    def send_test_message(self):
        try:
            print(f"🔄 Sending test message to {target_contact}...")
            if not self.find_and_select_contact():
                return False

            input_box = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div[contenteditable="true"][data-tab="10"]'))
            )
            input_box.click()
            input_box.send_keys(test_message)
            input_box.send_keys(Keys.ENTER)
            print(f"✅ Test message sent to {target_contact}")
            return True
        except Exception as e:
            print(f"❌ Failed to send test message: {str(e)}")
            return False

    def find_and_select_contact(self):
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//div[@aria-label="Chat list"]'))
            )
            chat_list = self.driver.find_elements(By.XPATH, '//div[@aria-label="Chat list"]//div[contains(@style,"z-index")]')
            
            for chat in chat_list:
                try:
                    name_element = chat.find_element(By.XPATH, './/span[@dir="auto"]')
                    if name_element.text == target_contact:
                        chat.click()
                        sleep(2)
                        return True
                except:
                    continue
            
            print(f"⚠️ Contact '{target_contact}' not found in chat list")
            return False
        except Exception as e:
            print(f"❌ Error finding contact: {str(e)}")
            return False

    def monitor_messages(self):
        try:
            while True:
                # Check if disconnected
                if self.check_no_connection():
                    print("❌ Tidak ada koneksi. Menunggu...")
                    self.was_disconnected = True
                    sleep(connection_check_interval)
                    continue

                # Check if reconnected
                if self.check_connection():
                    if self.was_disconnected:
                        print("🔁 Reconnected! Sending online message.")
                        self.send_test_message()
                        self.was_disconnected = False

                # Find contact
                if not self.find_and_select_contact():
                    print(f"⚠️ Contact '{target_contact}' not found.")
                    sleep(connection_check_interval)
                    continue

                # Check for new messages
                messages = self.driver.find_elements(By.XPATH, '//div[contains(@class,"message-in")]//span[@dir="ltr"]')
                latest_message = messages[-1].text.strip() if messages else ""

                if latest_message and latest_message != self.last_message:
                    self.last_message = latest_message
                    waktu = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    with open(rekap_file, "a", encoding="utf-8") as f:
                        f.write(f"{waktu} | {target_contact}: {latest_message}\n")

                    input_box = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, 'div[contenteditable="true"][data-tab="10"]'))
                    )
                    input_box.click()
                    input_box.send_keys("Selamat Datang")
                    input_box.send_keys(Keys.ENTER)

                    print(f"✅ New message from {target_contact} replied and logged")
                else:
                    print("🔍 No new messages")

                sleep(connection_check_interval)

        except KeyboardInterrupt:
            print("⛔ Stopped by user")
            if self.driver:
                self.driver.quit()
        except Exception as e:
            print(f"❗ Error: {str(e)}")
            if self.driver:
                self.driver.quit()

    def run(self):
        print("🚀 Starting WhatsApp Bot")
        try:
            while True:
                if not self.check_connection():
                    if not self.connect():
                        print(f"🔄 Retrying connection in {connection_check_interval} seconds...")
                        sleep(connection_check_interval)
                        continue

                self.monitor_messages()

        except KeyboardInterrupt:
            print("⛔ Stopped by user")
        finally:
            if self.driver:
                self.driver.quit()

if __name__ == "__main__":
    bot = WhatsAppBot()
    bot.run()
