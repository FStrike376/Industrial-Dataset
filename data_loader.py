import os
import sys
import requests
import pandas as pd

# Публичная ссылка на файл (Яндекс.Диск)
YANDEX_DISK_URL = "https://disk.yandex.ru/d/Uk1Lt-CmOnijEw"
# Имя файла, под которым сохраняем локально
LOCAL_FILE_NAME = "predictive_maintenance_v3.csv"


def download_file(url: str, dest_path: str) -> None:
    """
    Скачивает файл с Яндекс.Диска по публичной ссылке.
    
    :param url: публичная ссылка на файл
    :param dest_path: путь, куда сохранить файл
    """
    # Получаем прямую ссылку на скачивание через API Яндекс.Диска
    api_url = "https://cloud-api.yandex.net/v1/disk/public/resources/download"
    params = {"public_key": url}
    response = requests.get(api_url, params=params)
    response.raise_for_status()
    download_url = response.json()["href"]

    # Скачиваем файл
    print(f"Скачиваем файл с {url}...")
    with requests.get(download_url, stream=True) as r:
        r.raise_for_status()
        with open(dest_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    print(f"Файл сохранён: {dest_path}")


def load_data(file_path: str) -> pd.DataFrame:
    """
    Загружает датасет из CSV-файла и возвращает DataFrame.
    """
    df = pd.read_csv(file_path)
    return df


def print_first_rows(df: pd.DataFrame, n_rows: int = 10) -> None:
    """
    Выводит первые n_rows строк датасета в консоль.
    """
    print(f"Первые {n_rows} строк датасета:")
    print(df.head(n_rows))


if __name__ == "__main__":
    # Если файл ещё не скачан — скачиваем
    if not os.path.exists(LOCAL_FILE_NAME):
        try:
            download_file(YANDEX_DISK_URL, LOCAL_FILE_NAME)
        except Exception as e:
            print(f"Не удалось скачать файл: {e}")
            sys.exit(1)

    try:
        df = load_data(LOCAL_FILE_NAME)
        print_first_rows(df)
    except FileNotFoundError:
        print(f"Файл {LOCAL_FILE_NAME} не найден.")
        sys.exit(1)
    except pd.errors.ParserError:
        print("Ошибка при чтении CSV — файл повреждён.")
        sys.exit(1)
