import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle
from dateutil.parser import parse
from datetime import datetime, timedelta
import os
import calendar
import numpy as np

# ===================================================================
# PENGATURAN (Silakan ubah bagian ini sesuai kebutuhan)
# ===================================================================
EXCEL_FILE = "Data Tanggal.xlsx"
OUTPUT_FILENAME = "Jadwal_Barang_Gaya_iOS_Juli.png"

# Atur ke None agar menggunakan tahun asli dari file Excel.
FORCE_YEAR = None

# Palet warna untuk kalender (disesuaikan untuk titik event)
COLORS = {
    'header': '#333333',
    'weekend': '#999999',
    'weekday': '#333333',
    'today_highlight': '#FF3B30', # Merah khas iOS
    'sampai_gudang': '#34C759',   # Hijau
    'eta_etd': '#007AFF',        # Biru
    'proses_order': '#FF9500',   # Oranye
    'sni_release': '#AF52DE',    # Ungu
    'default_event': '#8E8E93'   # Abu-abu untuk event lain
}

# Pengaturan Font Profesional
plt.rcParams['font.family'] = 'sans-serif'
# ===================================================================

# --- Fungsi Bantuan ---
def convert_date(date_val):
    """Mengonversi nilai menjadi datetime, menangani error."""
    if pd.isna(date_val): return None
    try:
        dt = parse(str(date_val))
        return dt.replace(year=FORCE_YEAR) if FORCE_YEAR else dt
    except (ValueError, TypeError, OverflowError):
        return None

def get_event_color(label):
    """Mendapatkan warna berdasarkan label event."""
    label_lower = label.lower()
    if 'gudang' in label_lower: return COLORS['sampai_gudang']
    if 'eta' in label_lower or 'etd' in label_lower: return COLORS['eta_etd']
    if 'order' in label_lower: return COLORS['proses_order']
    if 'sni' in label_lower or 'publish' in label_lower: return COLORS['sni_release']
    return COLORS['default_event']

# --- Baca dan Proses Data dari Excel ---
if not os.path.exists(EXCEL_FILE):
    raise FileNotFoundError(f"File '{EXCEL_FILE}' tidak ditemukan.")

df_raw = pd.read_excel(EXCEL_FILE, header=None)
try:
    kode_barang = df_raw.iloc[4, 1:].values
    judul_event = df_raw.iloc[5:, 0].values
    data_tanggal = df_raw.iloc[5:, 1:]
except IndexError:
    raise ValueError("Struktur data di file Excel tidak sesuai.")

data = []
for idx, kode in enumerate(kode_barang):
    if pd.isna(kode): continue
    baris = {
        str(judul).strip(): convert_date(val)
        for judul, val in zip(judul_event, data_tanggal.iloc[:, idx].values) if not pd.isna(judul)
    }
    data.append(baris)
df = pd.DataFrame(data)

# --- Kelompokkan event berdasarkan tanggal ---
events_by_date = {}
for _, row in df.iterrows():
    for label, date_val in row.items():
        if not isinstance(date_val, datetime): continue
        date_key = date_val.date()
        if date_key not in events_by_date: events_by_date[date_key] = []
        events_by_date[date_key].append({'label': label})

# --- [REVISI] Pengaturan Kalender ---
# Fokus hanya pada bulan Juli di tahun saat ini.
today = datetime.now().date()
months_to_display = [(today.year, 7)] # Format: [(Tahun, Bulan)]

# --- Plot Kalender Gaya iOS ---
fig, axes = plt.subplots(len(months_to_display), 1, figsize=(6, 4 * len(months_to_display)), squeeze=False)
fig.tight_layout(pad=4.0)
axes = axes.flatten()

for i, (year, month) in enumerate(months_to_display):
    ax = axes[i]
    ax.set_title(f"{calendar.month_name[month].upper()} {year}", fontweight='bold', fontsize=16, color=COLORS['header'])
    
    # Sembunyikan sumbu dan bingkai
    ax.axis('off')
    ax.set_aspect('equal')
    ax.set_xlim(0, 7)
    ax.set_ylim(0, 7) # 1 baris untuk header + 6 baris untuk tanggal

    # Gambar header hari (S, S, R, K, J, S, M)
    day_headers = ['S', 'S', 'R', 'K', 'J', 'S', 'M']
    for d, header in enumerate(day_headers):
        ax.text(d + 0.5, 6.5, header, ha='center', va='center', fontsize=11, color=COLORS['header'], fontweight='medium')

    # Dapatkan matriks kalender
    month_cal = calendar.monthcalendar(year, month)
    
    for week_idx, week in enumerate(month_cal):
        y_pos = 5.5 - week_idx
        for day_idx, day in enumerate(week):
            if day == 0: continue
            x_pos = day_idx + 0.5
            
            date_key = datetime(year, month, day).date()
            
            # Tentukan warna tanggal
            day_color = COLORS['weekend'] if day_idx >= 5 else COLORS['weekday']
            
            # Sorot hari ini
            if date_key == today:
                ax.add_patch(Circle((x_pos, y_pos), 0.4, color=COLORS['today_highlight']))
                day_color = 'white'

            ax.text(x_pos, y_pos, str(day), ha='center', va='center', fontsize=14, color=day_color, fontweight='medium' if date_key == today else 'regular')
            
            # Tambahkan titik event
            if date_key in events_by_date:
                events_today = events_by_date[date_key]
                unique_colors = list(dict.fromkeys([get_event_color(e['label']) for e in events_today]))
                
                num_dots = len(unique_colors)
                dot_x_start = x_pos - (num_dots - 1) * 0.1
                for dot_idx, color in enumerate(unique_colors[:4]): # Maksimal 4 titik
                    ax.add_patch(Circle((dot_x_start + dot_idx * 0.2, y_pos - 0.35), 0.05, color=color))

# --- Tambahkan Legenda di Bawah ---
legend_ax = fig.add_axes([0, 0, 1, 0.05]) # Area untuk legenda
legend_ax.axis('off')
legend_elements = [
    Rectangle((0,0), 1, 1, color=c, label=l) for l, c in 
    [('Sampai Gudang', COLORS['sampai_gudang']),
     ('ETA/ETD', COLORS['eta_etd']),
     ('Proses Order', COLORS['proses_order']),
     ('SNI/Release', COLORS['sni_release'])]
]
legend_ax.legend(handles=legend_elements, loc='center', ncol=4, fontsize=10, frameon=False)


plt.savefig(OUTPUT_FILENAME, dpi=300, bbox_inches='tight')
plt.show()

print(f"Grafik kalender berhasil dibuat dan disimpan sebagai '{OUTPUT_FILENAME}'")
