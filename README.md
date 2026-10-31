# Industrial-Dataset

Синтетический набор данных для промышленного интернета вещей с 24 042 записями о станках с ЧПУ и сопутствующем оборудовании, предназначенный для предиктивного обслуживания, прогнозирования отказов и оценки остаточного срока службы в производственных условиях.

**Источник:** [Kaggle — Industrial Machine Predictive Maintenance](https://www.kaggle.com/datasets/tatheerabbas/industrial-machine-predictive-maintenance)

**Размер файла:** 2.1 МБ

[Скачать датасет (Яндекс.Диск)](https://disk.yandex.ru/d/Uk1Lt-CmOnijEw)

## Описание признаков

* `timestamp` — временная метка
* `machine\\\_id` — идентификатор станка
* `machine\\\_type` — тип оборудования (CNC, Pump, Compressor)
* `vibration\\\_rms` — среднеквадратичная вибрация
* `temperature\\\_motor` — температура двигателя
* `current\\\_phase\\\_avg` — средний ток фазы
* `pressure\\\_level` — уровень давления
* `rpm` — обороты в минуту
* `operating\\\_mode` — режим работы (idle, normal, peak)
* `hours\\\_since\\\_maintenance` — часы с последнего обслуживания
* `ambient\\\_temp` — температура окружающей среды
* `rul\\\_hours` — остаточный ресурс в часах
* `failure\\\_within\\\_24h` — отказ в течение 24 часов (0/1)
* `failure\\\_type` — тип отказа (none, hydraulic, bearing, electrical, motor\_overheat)
* `estimated\\\_repair\\\_cost` — оценка стоимости ремонта

## Установка и запуск

1. Клонируйте репозиторий:

```
   git clone https://github.com/FStrike376/Industrial-Dataset.git
   cd Industrial-Dataset
```

2. Создайте виртуальное окружение и активируйте его:

```
   python -m venv .venv
```

Windows:

```
   .venv\\\\Scripts\\\\activate
```

Linux/macOS:

```
   source .venv/bin/activate
```

3. Установите зависимости:

```
   pip install -r requirements.txt
```

4. Запустите скрипт, передав путь к CSV-файлу аргументом:

```
   python data\\\_loader.py
```



## Анализ данных

Основной анализ находится в ноутбуке `EDA.ipynb`. В нём используются pandas и Plotly Express; графики настроены на PNG-рендеринг для отображения в GitHub. Для интерактивного просмотра локально можно временно переключить `pio.renderers.default` на `browser`.

