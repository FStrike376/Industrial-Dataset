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

   ```bash
   git clone https://github.com/FStrike376/Industrial-Dataset.git
   cd Industrial-Dataset
   ```

2. Создайте виртуальное окружение:

   ```bash
   python -m venv .venv
   ```

3. Активируйте окружение.

   **Windows (PowerShell):**

   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

   **Windows (cmd):**

   ```cmd
   .venv\Scripts\activate.bat
   ```

   **Linux/macOS:**

   ```bash
   source .venv/bin/activate
   ```

4. Установите зависимости:

   ```bash
   pip install -r requirements.txt
   ```

5. Загрузите датасет и запустите скрипт загрузчика:

   ```bash
   python data_loader.py
   ```

## Анализ данных

Основной анализ находится в ноутбуке `notebooks/EDA.ipynb`. В нём представлены восемь разделов исходного EDA и дополнительный раздел 9 «Продвинутая визуализация (Plotly)».

В ноутбуке по умолчанию установлен статический рендерер `"png"` (в первой ячейке с импортами: `pio.renderers.default = "png"`), что требует установленного пакета Kaleido и совместимого браузера Chrome/Chromium. Для интерактивного просмотра графиков поменяйте значение `pio.renderers.default` в ячейке с импортами на `"plotly_mimetype"` (для Jupyter/VS Code) или `"browser"` (для открытия в отдельной вкладке браузера):

```python
import plotly.io as pio
pio.renderers.default = "plotly_mimetype"  # или "browser"
```