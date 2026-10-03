# Industrial-Dataset

Синтетический набор данных для промышленного интернета вещей с 24 042 записями о станках с ЧПУ и сопутствующем оборудовании, предназначенный для предиктивного обслуживания, прогнозирования отказов и оценки остаточного срока службы в производственных условиях.

**Источник:** [Kaggle — Industrial Machine Predictive Maintenance](https://www.kaggle.com/datasets/tatheerabbas/industrial-machine-predictive-maintenance)

**Размер файла:** 2.1 МБ

[Скачать датасет (Яндекс.Диск)](https://disk.yandex.ru/d/Uk1Lt-CmOnijEw)

## Описание признаков

- `timestamp` — временная метка
- `machine_id` — идентификатор станка
- `machine_type` — тип оборудования (CNC, Pump, Compressor)
- `vibration_rms` — среднеквадратичная вибрация
- `temperature_motor` — температура двигателя
- `current_phase_avg` — средний ток фазы
- `pressure_level` — уровень давления
- `rpm` — обороты в минуту
- `operating_mode` — режим работы (idle, normal, peak)
- `hours_since_maintenance` — часы с последнего обслуживания
- `ambient_temp` — температура окружающей среды
- `rul_hours` — остаточный ресурс в часах
- `failure_within_24h` — отказ в течение 24 часов (0/1)
- `failure_type` — тип отказа (none, hydraulic, bearing, electrical, motor_overheat)
- `estimated_repair_cost` — оценка стоимости ремонта

## Установка и запуск

1. Клонируйте репозиторий:

   git clone https://github.com/FStrike376/Industrial-Dataset.git
   cd Industrial-Dataset

2. Создайте виртуальное окружение и активируйте его:

   python -m venv .venv

   Windows:
   .venv\Scripts\activate

   Linux/macOS:
   source .venv/bin/activate

3. Установите зависимости:

   pip install -r requirements.txt

4. Запустите скрипт, передав путь к CSV-файлу аргументом:

   python data_loader.py
