# Baca file sumber
with open('L.TXT', 'r', encoding='utf-8') as file:
    lines = file.readlines()

# Temukan baris yang mengandung 'S U R A T' dan 'J A L A N'
split_index = None
for i, line in enumerate(lines):
    clean_line = line.replace(" ", "").upper()
    if 'SURATJALAN' in clean_line:
        split_index = i
        break

# Validasi
if split_index is None:
    raise ValueError("Bagian 'S U R A T  J A L A N' tidak ditemukan dalam file.")

# Pisahkan isi file
invoice_lines = lines[:split_index]
surat_jalan_lines = lines[split_index:]

# Simpan ke dua file
with open('L-INV.TXT', 'w', encoding='utf-8') as f:
    f.writelines(invoice_lines)

with open('L-SJ.TXT', 'w', encoding='utf-8') as f:
    f.writelines(surat_jalan_lines)

print("✅ File berhasil dipisah jadi L-INV.TXT dan L-SJ.TXT")
