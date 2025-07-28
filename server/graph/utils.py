import requests
import os

def download_file(url, save_dir="downloads"):
    headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/114.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5"
}
    os.makedirs(save_dir, exist_ok=True)
    filename = os.path.basename(url.split("?")[0])  
    filepath = os.path.join(save_dir, filename)

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        with open(filepath, 'wb') as f:
            f.write(response.content)
        print(f"Downloaded: {filename}")
        return filepath
    else:
        print(f"Failed to download: {url}")
        print(f"[INFO] Status code: {response.status_code}")
        print(f"[INFO] Response headers: {response.headers}")
        return None
