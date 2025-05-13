# Concise Video Game Data Enhancement

This project enhances a basic video game dataset by adding three new informative fields using the Google AI Studio API:

- **Genre**: Single-word classification based on the game title.
- **Short Description**: A concise description of the game in under 30 words.
- **Player Mode**: Classification of gameplay mode into "Singleplayer", "Multiplayer", or "Both".

## 🔄 Process Overview

1. **Data Loading**:
   - The script loads a CSV file containing game titles and their thumbnail image URLs.

2. **Genre Classification**:
   - Each game's title is processed to generate a **single-word** genre label.
   - Examples:
     - "Call of Duty" → "Shooter"
     - "FIFA 23" → "Sports"

3. **Short Description Generation**:
   - A brief summary of each game is generated using a limit of 30 words.
   - Descriptions are designed to be short, informative, and not include the game title.

4. **Player Mode Identification**:
   - The script determines the player mode based on the game title, returning one of the following:
     - "Singleplayer"
     - "Multiplayer"
     - "Both"

5. **Data Processing with Resume Support**:
   - Supports resuming processing in case of failure or interruption.
   - Incorporates backoff handling for API rate limits.

6. **Output**:
   - The final DataFrame includes new columns: `genre`, `short_description`, and `player_mode`.
   - Results are saved to a new CSV file: `Enhanced_Game_Thumbnail_Final.csv`.

## 🔐 How to Set Up and Use Google AI Studio API

To use this script, you need an API key from Google AI Studio.

### ✨ Step-by-Step Guide:

1. **Create a Google Account** (if you don't have one).

2. **Go to Google AI Studio**:  
   [https://makersuite.google.com/app](https://makersuite.google.com/app)

3. **Get Your API Key**:
   - Click your profile picture → "Get API key"
   - Copy the generated key.

4. **Use the API Key in the Script**:
   Open the Python script and find this line:
   ```python
   API_KEY = "YOUR_API_KEY_HERE"
````

Replace `"YOUR_API_KEY_HERE"` with the key you copied.

5. **Run the Script**:

   * Make sure the file `Game Thumbnail.csv` is in the same directory.
   * Install dependencies if needed:

     ```bash
     pip install pandas google-generativeai tqdm
     ```
   * Run the script:

     ```bash
     python task2_enrich_games.py
     ```
```
---

## ✅ Sample Output Format

| game_title      | genre    | short_description                        | player_mode |
|-----------------|----------|------------------------------------------|-------------|
| Minecraft       | Sandbox  | A block-based world where players build. | Both        |
| FIFA 23         | Sports   | Realistic football simulation gameplay.  | Multiplayer |
| Call of Duty    | Shooter  | Military-themed action-packed shooting.  | Both        |
