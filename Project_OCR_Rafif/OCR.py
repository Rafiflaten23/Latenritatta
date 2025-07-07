import pytesseract
import cv2
import openpyxl
import re
import os

# 1️⃣ SETUP PATH TESSERACT
pytesseract.pytesseract.tesseract_cmd = r"C:\Users\Purchase (Arie)\Downloads\Laten\tesseract.exe"

# 2️⃣ SETUP FOLDER GAMBAR & OUTPUT
folder_gambar = r"C:\Users\Purchase (Arie)\Dropbox\SHERING PK ADRIAN\py_OCR img\Gambar"
folder_output = r"C:\Users\Purchase (Arie)\Dropbox\SHERING PK ADRIAN\py_OCR img\Hasil"

# 3️⃣ BUAT FILE EXCEL
wb = openpyxl.Workbook()
ws = wb.active
ws.title = "Data Produk"
ws.append(["Nama File", "Pcs/QTY", "Harga (Rp)", "OCR Gabungan"])

# 4️⃣ LOOP SETIAP GAMBAR
for nama_file in os.listdir(folder_gambar):
    if not nama_file.lower().endswith(('.png', '.jpg', '.jpeg')):
        continue

    path_gambar = os.path.join(folder_gambar, nama_file)
    img = cv2.imread(path_gambar)

    if img is None:
        print(f"❌ Gagal baca gambar: {nama_file}")
        continue

    # --- 🔹 OCR HITAM (Preprocessing) ---
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.bilateralFilter(gray, 9, 75, 75)
    gray = cv2.equalizeHist(gray)
    _, thresh_black = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    text_black = pytesseract.image_to_string(thresh_black, config='--psm 6')

    # --- 🔴 OCR MERAH (Mask HSV) ---
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    lower_red1 = (0, 70, 50)
    upper_red1 = (10, 255, 255)
    lower_red2 = (170, 70, 50)
    upper_red2 = (180, 255, 255)
    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    mask_red = cv2.bitwise_or(mask1, mask2)
    red_only = cv2.bitwise_and(img, img, mask=mask_red)
    gray_red = cv2.cvtColor(red_only, cv2.COLOR_BGR2GRAY)
    _, thresh_red = cv2.threshold(gray_red, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    text_red = pytesseract.image_to_string(thresh_red, config='--psm 6')

    # --- ⚪ OCR LANGSUNG TANPA PROSES ---
    text_raw = pytesseract.image_to_string(img, config='--psm 6')

    # --- 🔄 GABUNGKAN SEMUA TEKS ---
    text_full = text_black + "\n" + text_red + "\n" + text_raw

    # --- 🔍 EKSTRAK PCS / QTY ---
    pcs_match = re.search(r"(?:QTY|pcs)[\s:]*([0-9]{1,4})", text_full, re.IGNORECASE)
    pcs = int(pcs_match.group(1)) if pcs_match else None

    # --- 💰 EKSTRAK HARGA ---
    harga_match = re.search(r"Rp[:.\s]?\s?([\dOol.,]+)", text_full)
    if harga_match:
        harga_str = harga_match.group(1)
        harga_str = harga_str.replace("O", "0").replace("o", "0").replace("l", "1")
        harga_str = harga_str.replace(".", "").replace(",", "").strip()
        harga = int(harga_str) if harga_str.isdigit() else None
    else:
        harga = None

    # --- 💾 SIMPAN KE EXCEL ---
    ws.append([nama_file, pcs, harga, text_full.strip()])

    # --- 📝 LOG PER FILE ---
    if pcs is None or harga is None:
        print(f"⚠️  Gagal deteksi lengkap: {nama_file}")
    else:
        print(f"✅ {nama_file}: QTY = {pcs}, Harga = Rp{harga}")

# 5️⃣ SIMPAN EXCEL
output_excel = os.path.join(folder_output, "hasil_ocr_produk_v3.xlsx")
wb.save(output_excel)
print(f"\n✅ Selesai! Hasil disimpan di:\n{output_excel}")
