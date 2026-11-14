import logging
from pathlib import Path

import pandas as pd
import requests


logger = logging.getLogger(__name__)

YANDEX_DISK_URL = "https://disk.yandex.ru/d/Uk1Lt-CmOnijEw"
REQUEST_TIMEOUT = 30


def download_file(url: str, destination: Path) -> None:
    """Download dataset from Yandex Disk safely via a temporary .part file."""

    destination.parent.mkdir(parents=True, exist_ok=True)
    temp_destination = destination.with_suffix(destination.suffix + ".part")

    api_url = "https://cloud-api.yandex.net/v1/disk/public/resources/download"

    response = requests.get(
        api_url,
        params={"public_key": url},
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()

    download_url = response.json()["href"]

    try:
        with requests.get(
            download_url,
            stream=True,
            timeout=REQUEST_TIMEOUT,
        ) as download_response:
            download_response.raise_for_status()

            with temp_destination.open("wb") as file:
                for chunk in download_response.iter_content(chunk_size=8192):
                    if chunk:
                        file.write(chunk)

        temp_destination.replace(destination)
        logger.info("Файл успешно скачан: %s", destination)
    except Exception:
        if temp_destination.exists():
            temp_destination.unlink()
        raise


def extract(
    source: str | Path | None = None,
) -> pd.DataFrame:
    """Download, if necessary, and read the raw dataset."""

    if source is None:
        source = (
            Path(__file__).resolve().parents[2]
            / "data"
            / "raw"
            / "predictive_maintenance_v3.csv"
        )

    source = Path(source)

    if not source.exists():
        logger.info("Локальный файл не найден. Скачивание из Яндекс.Диска в %s...", source)
        download_file(YANDEX_DISK_URL, source)

    return pd.read_csv(source)
