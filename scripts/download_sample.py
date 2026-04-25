from pathlib import Path
import requests

FILE_ID = "15fMNCIAz5oRH_oj24HS9qBSRXKPMQ7uM"
URL = f"https://drive.usercontent.google.com/download?id={FILE_ID}&export=download&confirm=t"
OUT = Path("data/2022-11_DPIRD_slice.nc")

OUT.parent.mkdir(parents=True, exist_ok=True)
if OUT.exists() and OUT.stat().st_size > 0:
    print(f"already present: {OUT} ({OUT.stat().st_size} bytes)")
    raise SystemExit(0)

with requests.get(URL, stream=True, timeout=120) as r:
    r.raise_for_status()
    total = 0
    with OUT.open("wb") as f:
        for chunk in r.iter_content(chunk_size=1024 * 1024):
            if not chunk:
                continue
            f.write(chunk)
            total += len(chunk)
            print(f"downloaded {total} bytes", flush=True)

print(f"saved {OUT} ({OUT.stat().st_size} bytes)")
