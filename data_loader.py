import sys
import os
import pandas as pd


def load_data(file_path: str) -> pd.DataFrame:
    """
    Загружает датасет из CSV-файла и возвращает DataFrame.

    :param file_path: путь к CSV-файлу
    :return: DataFrame с данными
    :raises FileNotFoundError: если файл не найден
    :raises pd.errors.ParserError: если CSV повреждён
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Файл {file_path} не найден. Убедитесь, что он скачан.")

    df = pd.read_csv(file_path)
    return df


def print_first_rows(df: pd.DataFrame, n_rows: int = 10) -> None:
    """
    Выводит первые n_rows строк датасета в консоль.

    :param df: DataFrame с данными
    :param n_rows: количество строк для вывода (по умолчанию 10)
    """
    print(f"Первые {n_rows} строк датасета:")
    print(df.head(n_rows))


if __name__ == '__main__':
    # Путь передаётся аргументом командной строки:
    # python data_loader.py путь/к/файлу.csv
    if len(sys.argv) < 2:
        print("Использование: python data_loader.py <путь_к_CSV>")
        sys.exit(1)

    file_path = sys.argv[1]

    try:
        df = load_data(file_path)
        print_first_rows(df)
    except FileNotFoundError as e:
        print(f"Ошибка: {e}")
        sys.exit(1)
    except pd.errors.ParserError as e:
        print(f"Ошибка при чтении CSV: {e}")
        sys.exit(1)