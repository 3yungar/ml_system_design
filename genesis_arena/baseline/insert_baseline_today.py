# Данный скрипт отрабатывается планировщиком cron ежедневно, в результате чего добавляется информация о базовом уровне потребления
import numpy as np
import pandas as pd
import pickle
import os
from dotenv import load_dotenv
from data_wrapper import db_wrapper
from clickhouse_driver import Client
import datetime as dt

# Параметры предыдущего дня
end_date = dt.datetime.now()
start_date = end_date - dt.timedelta(days=1)
startYear, startMonth, startDay = start_date.year, start_date.month, start_date.day
endYear, endMonth, endDay = end_date.year, end_date.month, end_date.day

# Подключение к БД с правами на чтение
load_dotenv()

HOST = os.getenv('BASE_HOST')
USERNAME = os.getenv('USERNAME')
PASSWORD = os.getenv('BASE_PASSWORD')
CA = os.getenv('CA')
READONLY = os.getenv('BASE_READONLY')

wrap = db_wrapper.ClickHouseWrapper(host=HOST, user=USERNAME, password=PASSWORD, ca=CA)

sensors = [
# Потребление компрессоров
{
    "db": "genesis_arena", "name": "map12e_142", "measurement": "Total AP energy", 
    "channel": 2, "phase": 0, "name_in_df": "compressor1", "mode": "max-min"
},
{
    "db": "genesis_arena", "name": "map12e_142", "measurement": "Total AP energy",
    "channel": 3, "phase": 0, "name_in_df": "compressor2", "mode": "max-min"
},
{
    "db": "genesis_arena", "name": "map12e_142", "measurement": "Total AP energy",
    "channel": 4, "phase": 0, "name_in_df": "compressor3", "mode": "max-min"
},
{
    "db": "genesis_arena", "name": "map12e_145", "measurement": "Total AP energy",
    "channel": 1, "phase": 0, "name_in_df": "compressor4", "mode": "max-min"
},
# Внешняя температура
{
    "db": "genesis_arena", "name": "weather_owm", "measurement": "Temperature",
    "channel": 0, "phase": 0, "name_in_df": "temp_outside", "mode": "mean"
}
]

start = dt.datetime(startYear, startMonth, startDay, 0, 0, 0) - dt.timedelta(hours=3)
end = dt.datetime(endYear, endMonth, endDay, 0, 0, 0) - dt.timedelta(hours=3)
presample = dt.timedelta(days=1)

data = wrap.get_particular_sensors(start, end, sensors, presample_time=presample,  without_confidence=True)

data = (data
 .tz_localize(None)
 .reset_index(names='time')
 .assign(compressors=lambda df: df[['compressor1', 'compressor2', 'compressor3', 'compressor4']].sum(axis=1))
 .pipe(lambda df: df.drop(columns=['compressor1', 'compressor2', 'compressor3', 'compressor4']))
 )

sensors = [
# Температура льда
{
    "db": "genesis_arena", "name": "msw-v3_2", "measurement": "Temperature", 
    "channel": 0, "phase": 0, "name_in_df": "temp_ice", "mode": "mean" 
}
]

start = dt.datetime(startYear, startMonth, startDay, 0, 0, 0) - dt.timedelta(hours=3)
end = dt.datetime(endYear, endMonth, endDay, 0, 0, 0) - dt.timedelta(hours=3)
presample = dt.timedelta(minutes=1)

ice_df = wrap.get_particular_sensors(start, end, sensors, presample_time=presample,  without_confidence=True)
ice_df = ice_df.tz_localize(None).reset_index(names='time')

ice_df = (ice_df
 # Обработка аномальных значений
 .assign(temp_ice=lambda df: np.where(df['temp_ice'].between(-10, 3), df['temp_ice'], np.NaN))
 .assign(temp_ice=lambda df: df['temp_ice'].ffill())
 # Дифференцируем, экспоненциально сглаженный, ряд для нахождения заливки
 .assign(diff=lambda df: df['temp_ice'].ewm(span=60).mean().diff())
 .assign(flood=lambda df: np.where(df['diff'] > 0.03, 1, 0))
 # Создаем признак, чтобы подсчитать время между заливками
 .assign(diff_time=dt.timedelta(minutes=45))
 )

# Подсчет правильного количества заливок
ice_df.loc[ice_df['flood'] == 1, 'diff_time'] = ice_df.loc[ice_df['flood'] == 1, 'time'].diff().fillna(dt.timedelta(minutes=100))
ice_df.loc[ice_df['diff_time'] < dt.timedelta(minutes=45), 'flood'] = 0

flood_df = ice_df.groupby(pd.to_datetime(ice_df['time'].dt.date))[['flood']].sum().reset_index()
data = data.merge(flood_df, on='time')

model = pickle.load(open('models/baseline_polynominal_compressors.sav', 'rb'))
xpoly = pickle.load(open('models/poly_features.sav', 'rb'))

xfeatures = xpoly.fit_transform(data[['temp_outside', 'flood']])
data['baseline'] = model.predict(xfeatures)
data['baseline'] = np.where(data['baseline'] > data['compressors'], data['baseline'], data['compressors'])
data['economy'] = data['baseline'] - data['compressors']

# Подключаемся к БД с правами записи
HOST = os.getenv('SUDO_HOST')
USERNAME = os.getenv('USERNAME')
PASSWORD = os.getenv('SUDO_PASSWORD')
CA = os.getenv('CA')
READONLY = os.getenv('SUDO_READONLY')

client = Client(host=HOST, user=USERNAME, password=PASSWORD, ca_certs=CA, secure=True)

# Запись данных в БД
client.execute('use akarmanov_test_db')
client.insert_dataframe(
    'INSERT INTO "baseline" (time, baseline, compressors, economy, temp_outside, flood) values',
    data[['time', 'baseline', 'compressors', 'economy', 'temp_outside', 'flood']],
    settings=dict(use_numpy=True)
    )