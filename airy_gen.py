import json
import requests
from datetime import datetime

# Configuration
API_URL = 'https://api.airy.tv/api/v2.1.7/channels'
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

# Filenames
M3U_FILENAME = "airy_channels.m3u"
EPG_FILENAME = "airy_channels.xml"

# Updated User and Repo Details
GITHUB_USERNAME = "BuddyChewChew"
REPO_NAME = "airy-playlist-generator"
GITHUB_RAW_URL = f"https://raw.githubusercontent.com/{GITHUB_USERNAME}/{REPO_NAME}/main/{EPG_FILENAME}"

headers = {'user-agent': USER_AGENT}

def format_date(iso_str):
    """Converts Airy ISO format to XMLTV format: YYYYMMDDHHMMSS +0000"""
    if not iso_str:
        return ""
    try:
        # Standardize 'Z' to offset for fromisoformat
        clean_date = iso_str.replace('Z', '+00:00')
        dt = datetime.fromisoformat(clean_date)
        return dt.strftime('%Y%m%d%H%M%S +0000')
    except Exception:
        return ""

def fetch_data():
    try:
        response = requests.get(API_URL, headers=headers, timeout=30)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching Airy data: {e}")
        return None

def generate_files(data):
    if not data or 'status' not in data or data['status'] != 'success':
        print("Invalid data received from API")
        return

    m3u_lines = [f'#EXTM3U x-tvg-url="{GITHUB_RAW_URL}"']
    xml_lines = ['<?xml version="1.0" encoding="UTF-8"?>', '<tv>']
    processed_channels = set()

    categories = data.get('response', {}).get('categories', [])

    for category in categories:
        # Clean up underscores in category names
        cat_name = category.get('name', 'General').replace('_', ' ')
        
        for chan in category.get('stream_channels', []):
            chan_id = str(chan.get('id', ''))
            if not chan_id or chan_id in processed_channels:
                continue
            
            # Clean up underscores in channel names
            chan_name = chan.get('name', 'Unknown').replace('_', ' ')
            stream_url = chan.get('source_url', '')
            if not stream_url:
                continue

            logo = chan.get('image_url', '')
            
            # M3U Entry
            m3u_lines.append(f'#EXTINF:-1 tvg-id="airy-{chan_id}" tvg-name="{chan_name}" tvg-logo="{logo}" group-title="{cat_name}",{chan_name}')
            m3u_lines.append(stream_url)

            # XML Channel Entry
            xml_lines.append(f'  <channel id="airy-{chan_id}">\n    <display-name>{chan_name}</display-name>\n    <icon src="{logo}" />\n  </channel>')
            
            # Parse Broadcasts for EPG
            broadcasts = chan.get('broadcasts', [])
            for prog in broadcasts:
                start_raw = prog.get('view_start_at_iso')
                duration = prog.get('view_duration', 0)
                
                start_fmt = format_date(start_raw)
                if not start_fmt:
                    continue

                # Calculate end time
                try:
                    start_dt = datetime.fromisoformat(start_raw.replace('Z', '+00:00'))
                    end_dt = datetime.fromtimestamp(start_dt.timestamp() + duration)
                    stop_fmt = end_dt.strftime('%Y%m%d%H%M%S +0000')
                except:
                    stop_fmt = ""

                title = (prog.get('title') or chan_name).replace('&', '&amp;')
                desc = (prog.get('description') or "No description available.").replace('&', '&amp;')

                if start_fmt and stop_fmt:
                    xml_lines.append(f'  <programme start="{start_fmt}" stop="{stop_fmt}" channel="airy-{chan_id}">')
                    xml_lines.append(f'    <title>{title}</title>\n    <desc>{desc}</desc>\n  </programme>')

            processed_channels.add(chan_id)

    xml_lines.append('</tv>')

    # Write Files to root
    with open(M3U_FILENAME, "w", encoding="utf-8") as f:
        f.write("\n".join(m3u_lines))
    with open(EPG_FILENAME, "w", encoding="utf-8") as f:
        f.write("\n".join(xml_lines))
    
    print(f"Successfully generated {M3U_FILENAME} and {EPG_FILENAME} in root directory.")

if __name__ == "__main__":
    generate_files(fetch_data())
