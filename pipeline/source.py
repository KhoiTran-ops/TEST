"""CafeF dataset adapter supporting HTTP CSV/ZIP and local files."""
from __future__ import annotations
from pathlib import Path
import shutil
import urllib.request
import zipfile


class CafeFSource:
    def __init__(self, url: str | None, raw_dir: Path, extracted_dir: Path):
        self.url, self.raw_dir, self.extracted_dir = url, raw_dir, extracted_dir

    def available(self) -> bool:
        if not self.url: return False
        if self.url.startswith(("http://", "https://")):
            try:
                req = urllib.request.Request(self.url, method="HEAD"); return urllib.request.urlopen(req, timeout=10).status < 400
            except OSError: return False
        return Path(self.url.removeprefix("file://")).exists()

    def download(self) -> Path:
        if not self.url: raise RuntimeError("SOURCE_UNAVAILABLE: configure CAFEF_DATASET_URL")
        self.raw_dir.mkdir(parents=True, exist_ok=True); name = Path(self.url).name or "cafef.csv"; target = self.raw_dir / name
        if self.url.startswith(("http://", "https://")): urllib.request.urlretrieve(self.url, target)
        else: shutil.copy2(Path(self.url.removeprefix("file://")), target)
        return target

    def extract(self, path: Path) -> list[Path]:
        self.extracted_dir.mkdir(parents=True, exist_ok=True)
        if zipfile.is_zipfile(path):
            with zipfile.ZipFile(path) as archive: archive.extractall(self.extracted_dir)
            return list(self.extracted_dir.glob("*.csv"))
        return [path]
