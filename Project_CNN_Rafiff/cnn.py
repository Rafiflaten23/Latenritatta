import tensorflow as tf
import numpy as np
from tensorflow.keras.utils import load_img, img_to_array
from openpyxl import Workbook
import os
import shutil

# === 1. Load Model CNN ===
model = tf.keras.models.load_model('model.h5')

# === 2. Daftar class sesuai pelatihan (tambahkan .png jika perlu) ===
class_names = [
    'ANIMAL-DINO-FIGUR.png','ANIMAL-FIGUR.png','ANIMAL-KARET.png','ANIMAL-WIND.png','BABY-GANTUNG.png',
    'BABY-KERINCING.png','BABY-TEETHER.png','BABY-TOY.png','BALON-AIR.png','BALON-TIUP.png',
    'BIG-SCOOTER.png','BIG-SKATE.png','BOARD-CARD.png','BOARD-CHESS.png','BOARD-DART.png',
    'BOARD-DOMINO.png','BOARD-LUDO.png','BOARD-MONOPOLY.png','BOARD-SCRABBLE.png','BOARD-STAKO.png',
    'BOARD-ULAR.png','BOLA-KARET.png','BOLA-KELERENG.png','BONEKA-BABY.png','BONEKA-BARBIE.png',
    'BONEKA-RUMAHAN.png','BONEKA-RUMAHAN-SYLVANIA.png','DANCE-DINO.png','DANCE-HEWAN.png',
    'DANCE-KAPAL.png','DANCE-KARAKTER.png','DANCE-MOBIL.png','DANCE-ROBOT.png','DANCE-TRANSFORMER.png',
    'DANCE-TUMBLING.png','DIY-BEADS.png','DIY-LILIN.png','DIY-PASIR.png','DIY-SLIME.png',
    'EDU-DRAWINGBOARD.png','EDU-IPAD.png','EDU-MAGNETBOARD.png','EDU-PROYEKTOR.png','EDU-PUZZLE.png',
    'EDU-RUBRIKS.png','FIDGET-LAINNYA.png','FIDGET-SPRING.png','FIDGET-SQUISHY.png',
    'FIGUR-KARAKTER.png','FIGUR-LAINNYA.png','GAME-ATM.png','GAME-CLAW.png','GAME-FISHING.png',
    'GAME-GIGIT.png','GAME-INTERAKSI.png','GAME-MARBLERUN.png','GAME-TANGGA-SELUNCUR.png',
    'GAME-TETRIS.png','GAME-TIRUSUARA.png','GAME-VENDING.png','GAME-WATERGAME.png','GAME-WHACAMOLE.png',
    'INTERAKSI-GASING.png','INTERAKSI-JAMTANGAN.png','INTERAKSI-PET.png','INTERAKSI-TAMIYA.png',
    'INTERAKSI-YOYO.png','KERETA.png','KERETA-ASEP.png','KITCHEN-CASHREGISTER.png','KITCHEN-SATUAN.png',
    'KITCHEN-SET.png','KITCHEN-TAS.png','KITCHEN-TROLLY.png','LAINNYA.png',
    'LEGO-ACTION (Robot, Dragon, Super hero, transformer).png','LEGO-ANIMALS.png',
    'LEGO-BATA.png','LEGO-BUILDINGS.png','LEGO-CHARACTER (figurine).png','LEGO-FLOWERS.png',
    'LEGO-OTHER.png','LEGO-OTOMOTIF.png','MOBIL-BUS-KERETA.png','MOBIL-KAPAL.png','MOBIL-SATUAN.png',
    'MOBIL-SATUAN-LAINNYA.png','MOBIL-SET.png','MOBIL-SET-LAINNYA.png','MOBIL-TRACKELECTRIC.png',
    'MOBIL-TRACKHOTWHEEL.png','MOBIL-TRACKMANUAL.png','MOBIL-TRANSFORMER.png','MUSIKAL-DRUM.png',
    'MUSIKAL-GITAR.png','MUSIKAL-LAINNYA.png','MUSIKAL-MIC.png','MUSIKAL-ORGAN.png',
    'MUSIKAL-XYLOPHONE.png','PISTOL-BATRE.png','PISTOL-BUBBLEBATRE.png','PISTOL-BUBBLEISI.png',
    'PISTOL-BUBBLESTICK.png','PISTOL-KRETEK.png','PISTOL-LAINNYA.png','PISTOL-SOFTEVA.png',
    'PISTOL-STICKY.png','PISTOL-WATER.png','PISTOL-WATERBOMB.png','PLAYSET-DOKTER.png',
    'PLAYSET-HERO.png','PLAYSET-MAKEUP.png','PLAYSET-RUMAHAN.png','PLAYSET-TOOLS.png',
    'PLAYSET-WALKIETALKIE.png','RC-DRONE.png','RC-LAINNYA.png','RC-OFFROAD.png','RC-SEDAN.png',
    'RC-TRANSFORMER.png','RC-TRUK.png','SPORT-BASKET.png','SPORT-BOWLING.png','SPORT-BOXING.png',
    'SPORT-HOCKEY.png','SPORT-HULAHOOP.png','SPORT-LAINNYA.png','SPORT-PANAH.png','SPORT-PEDANG.png',
    'SPORT-POOL.png','SPORT-SKIPPING.png','SPORT-SOCCER.png','SPORT-TENDA.png','SPORT-TEROPONG.png',
    'SWIM-GLASSES.png','SWIM-POOL.png','SWIM-TIRE.png','SWIM-TOY.png','SWIM-VEST.png'
]

# === 3. Konfigurasi gambar & path folder ===
img_height, img_width = 224, 224  # Harus sesuai dengan model
input_folder = 'test_input'
output_folder = 'hasil_output'
os.makedirs(output_folder, exist_ok=True)

# === 4. Buat workbook Excel untuk mencatat hasil ===
wb = Workbook()
ws = wb.active
ws.title = "Prediksi"
ws.append(["Nama File", "Kategori Prediksi"])

# === 5. Prediksi semua gambar ===
image_files = [f for f in os.listdir(input_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
total = len(image_files)

for i, filename in enumerate(image_files, start=1):
    filepath = os.path.join(input_folder, filename)
    print(f"[{i}/{total}] Memproses: {filename}")

    try:
        # Preprocessing gambar
        img = load_img(filepath, target_size=(img_height, img_width))
        img_array = img_to_array(img)
        img_array = tf.expand_dims(img_array, 0) / 255.0  # Normalisasi ke 0-1

        # Prediksi
        pred = model.predict(img_array, verbose=0)
        predicted_class = class_names[np.argmax(pred)]

        # Buat folder berdasarkan prediksi jika belum ada
        target_dir = os.path.join(output_folder, predicted_class)
        os.makedirs(target_dir, exist_ok=True)

        # Salin gambar ke folder prediksi
        shutil.copy(filepath, os.path.join(target_dir, filename))

        # Catat ke Excel
        ws.append([filename, predicted_class])
        print(f"✅ {filename} → {predicted_class}")

    except Exception as e:
        print(f"❌ Error saat memproses {filename}: {e}")
        ws.append([filename, "ERROR"])

# === 6. Simpan Excel ke folder output ===
excel_path = os.path.join(output_folder, "hasil_prediksi.xlsx")
wb.save(excel_path)
print(f"\n📊 File hasil prediksi disimpan di: {excel_path}")
