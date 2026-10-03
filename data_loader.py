import pandas as pd
import os


def load_and_print_data(file_path: str, n_rows: int = 10) -> None:
    """
    Загружает датасет и выводит первые n_rows строк в консоль.

    :param file_path: путь к CSV-файлу
    :param n_rows: количество строк для вывода (по умолчанию 10)
    """
    if not os.path.exists(file_path):
        print(f"Файл {file_path} не найден. Убедитесь, что он скачан.")
        return

    try:
        df = pd.read_csv(file_path)
        print(f"Первые {n_rows} строк датасета:")
        print(df.head(n_rows))
    except Exception as e:
        print(f"Ошибка при чтении файла: {e}")


if __name__ == '__main__':
    load_and_print_data('C:/data/predictive_maintenance_v3.csv')