import urllib.request
import os
import sys

def download():
    url = 'https://huggingface.co/cross-encoder/nli-deberta-v3-small/resolve/main/model.safetensors'
    dest_dir = 'C:/Users/VICTUS/.cache/huggingface/hub/models--cross-encoder--nli-deberta-v3-small/snapshots/fa2804872c3b4bd748f38c0185cc85775361e735'
    dest = os.path.join(dest_dir, 'model.safetensors')
    tmp = dest + '.tmp'

    if os.path.exists(dest) and os.path.getsize(dest) > 100_000_000:
        print(f"Already exists: {dest} ({os.path.getsize(dest)} bytes)")
        return

    print("Connecting to Hugging Face CDN...")
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    with urllib.request.urlopen(req, timeout=30) as res:
        total = int(res.headers.get('Content-Length', 0))
        print(f"Total model file size: {round(total / (1024*1024), 2)} MB")
        downloaded = 0
        chunk_size = 2 * 1024 * 1024  # 2MB chunks
        last_pct = -1

        with open(tmp, 'wb') as f:
            while True:
                chunk = res.read(chunk_size)
                if not chunk:
                    break
                f.write(chunk)
                downloaded += len(chunk)
                pct = int((downloaded / total) * 100) if total else 0
                if pct % 10 == 0 and pct != last_pct:
                    print(f"  -> {pct}% ({round(downloaded / (1024*1024), 1)} MB / {round(total / (1024*1024), 1)} MB)", flush=True)
                    last_pct = pct

    if os.path.exists(dest):
        os.remove(dest)
    os.rename(tmp, dest)
    print("Download completed successfully!")

if __name__ == '__main__':
    download()
