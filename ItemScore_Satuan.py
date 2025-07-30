import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
import os

# --- 1. Load data Excel ---
df = pd.read_excel("Data.xlsx")
df.columns = df.columns.str.strip()

# --- 2. Identifikasi kolom bulan ---
month_cols = df.columns[2:]
n_months = len(month_cols)
date_range = pd.date_range(start="2022-01-01", periods=n_months, freq="MS")

# --- 3. Pisahkan stok dan penjualan ---
stok_df = df[df['Tipe'].str.lower() == 'stok'].set_index('Kategori')
penjualan_df = df[df['Tipe'].str.lower() == 'penjualan'].set_index('Kategori')

stok_df = stok_df.iloc[:, 0:n_months].apply(pd.to_numeric, errors='coerce').fillna(0)
penjualan_df = penjualan_df.iloc[:, 0:n_months].apply(pd.to_numeric, errors='coerce').fillna(0)

stok_df.columns = date_range
penjualan_df.columns = date_range

common_kategori = stok_df.index.intersection(penjualan_df.index)

# --- 4. ABC Classification ---
total_all_penjualan = penjualan_df.select_dtypes(include='number').sum().sum()
sorted_contribution = penjualan_df.sum(axis=1).sort_values(ascending=False)
cumulative_contribution = sorted_contribution.cumsum() / total_all_penjualan

abc_map = {}
for val in cumulative_contribution.index:
    rank = cumulative_contribution[val]
    if rank <= 0.2:
        abc_map[val] = ('A', 100)
    elif rank <= 0.5:
        abc_map[val] = ('B', 70)
    else:
        abc_map[val] = ('C', 40)

# --- 5. Hitung skor tiap kategori ---
results = []
turnover_list = []

for kategori in common_kategori:
    stok_vals = stok_df.loc[kategori].values
    penjualan_vals = penjualan_df.loc[kategori].values

    total_penjualan = np.sum(penjualan_vals)
    avg_stok = np.mean(stok_vals)
    turnover = total_penjualan / avg_stok if avg_stok > 0 else 0
    turnover_list.append(turnover)

# Dihitung di luar agar bisa dibandingkan
max_turnover = max(turnover_list)

for i, kategori in enumerate(common_kategori):
    stok_vals = stok_df.loc[kategori].values
    penjualan_vals = penjualan_df.loc[kategori].values

    total_penjualan = np.sum(penjualan_vals)
    avg_stok = np.mean(stok_vals)
    turnover = turnover_list[i]

    x = np.arange(len(penjualan_vals)).reshape(-1, 1)
    y = penjualan_vals.reshape(-1, 1)
    model = LinearRegression().fit(x, y)
    trend = model.coef_[0][0]

    aktif_bulan = (stok_vals > 0) | (penjualan_vals > 0)
    availability_ratio = ((stok_vals > 0) & aktif_bulan).sum() / aktif_bulan.sum() if aktif_bulan.sum() > 0 else 0
    sales_consistency = (penjualan_vals > 0).sum() / len(penjualan_vals)
    abc_class, abc_score = abc_map.get(kategori, ('C', 40))

    # --- Skor dengan log scale untuk turnover ---
    turnover_score = min(np.log1p(turnover) / np.log1p(10), 1.0) * 100
    trend_score = min(max(trend / 5, 0), 1.0) * 100
    availability_score = availability_ratio * 100
    consistency_score = sales_consistency * 100

    final_score = (
        turnover_score * 0.35 +
        trend_score * 0.20 +
        availability_score * 0.15 +
        consistency_score * 0.15 +
        abc_score * 0.15
    )

    results.append({
        'Kategori': kategori,
        'Total Penjualan': int(total_penjualan),
        'Avg Stok': round(avg_stok, 2),
        'Turnover Score': round(turnover_score, 2),
        'Trend Score': round(trend_score, 2),
        'Availability Score': round(availability_score, 2),
        'Consistency Score': round(consistency_score, 2),
        'ABC Class': abc_class,
        'ABC Score': abc_score,
        'Item Score Final': round(final_score, 2)
    })

# --- 6. Buat DataFrame hasil ---
df_result = pd.DataFrame(results).sort_values(by='Item Score Final', ascending=False)

# --- 7. Tambahkan Stok Terakhir dan Status Stok ---
last_month = stok_df.columns[-1]  # Juni 2025
stok_terakhir = stok_df[last_month]
df_result['Stok Terakhir'] = df_result['Kategori'].map(stok_terakhir)

df_result['Status Stok'] = df_result['Stok Terakhir'].apply(
    lambda x: '⚠️ Mau Habis' if x < 10 else '✅ Aman'
)

# --- 8. Simpan ke Excel ---
df_result.to_excel("ItemScore_Final_NetralStock.xlsx", index=False)

# --- 9. Grafik tren penjualan tahunan (Top 5) ---
penjualan_tahunan = penjualan_df.groupby(penjualan_df.columns.year, axis=1).sum()

plt.figure(figsize=(10, 6))
for kategori in penjualan_tahunan.index[:5]:
    plt.plot(penjualan_tahunan.columns, penjualan_tahunan.loc[kategori], label=kategori)

plt.title("📈 Tren Penjualan Tahunan (Top 5 Kategori)")
plt.xlabel("Tahun")
plt.ylabel("Total Penjualan")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.close()

# --- 10. Grafik tren untuk semua kategori ---
os.makedirs("Tren_Per_Kategori", exist_ok=True)

for kategori in penjualan_df.index:
    yearly = penjualan_df.loc[kategori].groupby(penjualan_df.columns.year).sum()

    plt.figure(figsize=(6, 4))
    plt.plot(yearly.index, yearly.values, marker='o', color='steelblue')
    plt.title(f"Tren Penjualan Tahunan - {kategori}")
    plt.xlabel("Tahun")
    plt.ylabel("Total Penjualan")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(f"Tren_Per_Kategori/tren_{kategori}.png")
    plt.close()
