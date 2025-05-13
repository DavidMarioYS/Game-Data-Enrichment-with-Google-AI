import pandas as pd
import google.generativeai as genai
import os
import time
import random
from tqdm import tqdm
import re

# ===============================
# STEP 1 – API Key & Konfigurasi
# ===============================
print("🔑 Mengkonfigurasi model dengan API key...")

# Masukkan API key secara langsung di sini
API_KEY = "AIzaSyDpP8m0pLSjffUlCHBFeyFHYRp1Hd4zEHQ"  # GANTI DENGAN API KEY ANDA

genai.configure(api_key=API_KEY)
model_name = 'gemini-1.5-flash-latest'
model = genai.GenerativeModel(model_name)

# ===============================
# STEP 2 – Load Dataset
# ===============================
print("📊 Memuat dataset...")
try:
    file_path = "Game Thumbnail.csv"
    df = pd.read_csv(file_path)
    print(f"✅ Dataset berhasil dimuat dengan {len(df)} baris data.")
except FileNotFoundError:
    raise FileNotFoundError(f"File {file_path} tidak ditemukan.")
except Exception as e:
    raise Exception(f"Error saat memuat file: {e}")

if 'game_title' not in df.columns:
    raise ValueError("Kolom 'game_title' tidak ditemukan di CSV.")

# ===============================
# STEP 3 – Definisikan Fungsi Prompt dengan Backoff
# ===============================
def safe_generate_content(model, prompt, max_retries=5, initial_delay=1):
    for attempt in range(max_retries):
        try:
            response = model.generate_content(prompt)
            return response
        except Exception as e:
            print(f"⚠️ Percobaan ke-{attempt + 1} gagal: {e}")
            if "429" in str(e):
                delay = (initial_delay * (2 ** attempt)) + random.uniform(0, 1)
                print(f"⏳ Menunggu {delay:.2f} detik sebelum mencoba lagi...")
                time.sleep(delay)
            else:
                raise  # Re-raise error jika bukan masalah rate limit
    print(f"❌ Gagal mendapatkan respons setelah {max_retries} percobaan.")
    return None

def get_genre(title):
    prompt = f"""Based on the title '{title}', classify the video game into a single genre.
    Give me exactly ONE WORD as your answer - no explanation, no punctuation, no additional words.
    Examples:
    - "Call of Duty" → "Shooter"
    - "FIFA 23" → "Sports"
    - "Minecraft" → "Sandbox"
    Your single-word answer:"""

    response = safe_generate_content(model, prompt)
    if response and hasattr(response, "text"):
        genre = re.sub(r'[^\w\s]', '', response.text.strip()).split()[0]
        return genre
    return "Unknown"

def get_description(title):
    prompt = f"""Write a concise description for the video game '{title}' in UNDER 30 WORDS.
    Keep it short and informative.
    Do not use more than 30 words.
    Do not include the title in your description."""

    response = safe_generate_content(model, prompt)
    if response and hasattr(response, "text"):
        description = response.text.strip()
        words = description.split()
        if len(words) > 30:
            description = ' '.join(words[:30])
        return description
    return "Description unavailable"

def get_player_mode(title):
    prompt = f"""Determine if the video game '{title}' is primarily:
    - Singleplayer
    - Multiplayer
    - Both (has significant single and multiplayer modes)

    Respond with EXACTLY ONE of these three options: "Singleplayer", "Multiplayer", or "Both".
    No explanation, just the word."""

    response = safe_generate_content(model, prompt)
    if response and hasattr(response, "text"):
        text = response.text.strip().lower()
        if "singleplayer" in text or "single player" in text:
            return "Singleplayer"
        elif ("multiplayer" in text or "multi player" in text) and "singleplayer" not in text and "single player" not in text:
            return "Multiplayer"
        elif "both" in text or (("multiplayer" in text or "multi player" in text) and ("singleplayer" in text or "single player" in text)):
            return "Both"
    return "Unknown"

# ===============================
# STEP 4 – Proses Data dengan Resume dan Backoff
# ===============================
print("⚙️ Memulai pemrosesan data...")

# Periksa apakah ada kolom yang sudah diproses sebelumnya
if 'genre' in df.columns and 'short_description' in df.columns and 'player_mode' in df.columns:
    print("📋 Data yang sudah diproses ditemukan, melanjutkan dari data yang ada...")
    genres = df['genre'].tolist()
    descriptions = df['short_description'].tolist()
    modes = df['player_mode'].tolist()
else:
    genres = [""] * len(df)
    descriptions = [""] * len(df)
    modes = [""] * len(df)

# Proses hanya baris yang belum memiliki data lengkap
for i, row in tqdm(df.iterrows(), total=len(df), desc="Memproses game"):
    title = row['game_title']

    # Skip jika semua data sudah ada dan valid
    if (i < len(genres) and genres[i] not in ["", "Unknown", "N/A"] and
            i < len(descriptions) and descriptions[i] not in ["", "Description unavailable", "N/A"] and
            i < len(modes) and modes[i] not in ["", "Unknown", "N/A"]):
        continue

    try:
        # Proses genre jika belum ada
        if i >= len(genres) or genres[i] in ["", "Unknown", "N/A"]:
            genres[i] = get_genre(title)

        # Proses deskripsi jika belum ada
        if i >= len(descriptions) or descriptions[i] in ["", "Description unavailable", "N/A"]:
            descriptions[i] = get_description(title)

        # Proses mode pemain jika belum ada
        if i >= len(modes) or modes[i] in ["", "Unknown", "N/A"]:
            modes[i] = get_player_mode(title)

        # Jeda waktu setelah setiap game diproses (bukan per permintaan individual)
        time.sleep(2) # Anda bisa menyesuaikan nilai ini

        # Simpan hasil secara berkala
        if i % 10 == 0 and i > 0:
            temp_df = df.copy()
            temp_df['genre'] = genres
            temp_df['short_description'] = descriptions
            temp_df['player_mode'] = modes
            temp_df.to_csv("Enhanced_Game_Thumbnail_temp.csv", index=False)
            print(f"💾 Progres disimpan ({i}/{len(df)})")

    except Exception as e:
        print(f"⚠️ Gagal memproses '{title}': {e}")
        # Pastikan semua daftar memiliki nilai, bahkan jika gagal
        if i >= len(genres) or not genres[i]:
            genres[i] = "Unknown"
        if i >= len(descriptions) or not descriptions[i]:
            descriptions[i] = "Description unavailable"
        if i >= len(modes) or not modes[i]:
            modes[i] = "Unknown"

# ===============================
# STEP 5 – Simpan ke CSV Baru
# ===============================
df['genre'] = genres
df['short_description'] = descriptions
df['player_mode'] = modes

output_path = "Enhanced_Game_Thumbnail_Final.csv"
df.to_csv(output_path, index=False)

print(f"✅ Selesai! Data disimpan ke: {output_path}")

# Tampilkan beberapa contoh hasil
print("\n📊 Contoh hasil:")
print(df[['game_title', 'genre', 'short_description', 'player_mode']].head())