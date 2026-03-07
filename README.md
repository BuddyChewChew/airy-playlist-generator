# Airy TV Playlist Generator

Automated scraper for Airy TV channels and EPG data.

## 🔗 URLs for IPTV Players

**M3U Playlist:**
`https://raw.githubusercontent.com/BuddyChewChew/airy-playlist-generator/main/airy_channels.m3u`

**EPG (Guide) URL:**
`https://raw.githubusercontent.com/BuddyChewChew/airy-playlist-generator/main/airy_channels.xml`

## 🛠️ How it Works
1. **Scraper:** `airy_gen.py` fetches the latest channel list and schedule from Airy TV's API.
2. **Automation:** GitHub Actions runs this script every 6 hours.
3. **Deployment:** The generated `.m3u` and `.xml` files are pushed directly to the `main` branch.

## 🚀 Setup
- No manual work required. 
- Ensure the repository remains public for the raw links to work in external players.
