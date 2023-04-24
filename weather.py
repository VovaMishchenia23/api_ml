import requests
import pandas as pd
import datetime
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("WEATHER_API_KEY")

LOCATION = "Kyiv"
DATA__FOLDER = "data/"
LVIV_ID = "33393099999"
SUMY_ID = "33275099999"
WEATHER_URL = os.getenv("WEATHER_URL")
PREDICTION_DURATION = 12
TIME_FORMAT = 24
problem_city_id = {"Lviv": LVIV_ID, "Sumy": SUMY_ID}
DAY_COLUMNN_NAMES = ['day_tempmax', 'day_tempmin', 'day_temp', 'day_dew', 'day_humidity',
                     'day_precip',
                     'day_precipcover', 'day_solarradiation', 'day_solarenergy', 'day_uvindex', 'day_moonphase']
HOUR_COLUMN_NAMES = ['hour_temp', 'hour_humidity', 'hour_dew', 'hour_precip', 'hour_precipprob', 'hour_snowdepth',
                     'hour_windgust', 'hour_windspeed', 'hour_winddir', 'hour_pressure', 'hour_visibility',
                     'hour_cloudcover', 'hour_solarradiation', 'hour_uvindex', 'hour_severerisk', 'hour_conditions']
ADDITIONAL_COLUMN_NAMES = ['location', 'time', 'date']
ADDITIONAL_COLUMN_NAMES_2 = ['region_id', 'is_weekend']


def get_all_regions_list():
    region_df = pd.read_csv(f"{DATA__FOLDER}regions.csv")
    locations = list(region_df["center_city_en"].values)
    locations.remove("Simferopol")
    locations.remove("Luhansk")
    return locations


def get_start_hour_prediction():
    return int(datetime.datetime.now().strftime("%H")) + 1


def get_weather(region="all"):
    region_df = pd.read_csv(f"{DATA__FOLDER}regions.csv")
    if region == "all":
        locations = get_all_regions_list()
    else:
        locations = [region]

    weather_df = pd.DataFrame(
        columns=ADDITIONAL_COLUMN_NAMES + DAY_COLUMNN_NAMES + HOUR_COLUMN_NAMES + ADDITIONAL_COLUMN_NAMES_2)
    start_hour_prediction = get_start_hour_prediction()
    end_hour_prediction = start_hour_prediction + PREDICTION_DURATION

    for location in locations:
        if location in problem_city_id:
            url = f'{WEATHER_URL}{problem_city_id[location]}'
        else:
            url = f'{WEATHER_URL}{location}'
        params = {
            'unitGroup': 'metric',
            'key': API_KEY,
            'include': 'hours'
        }
        response = requests.get(url, params=params).json()

        for hour in range(start_hour_prediction, end_hour_prediction):
            day_info = response['days'][hour // TIME_FORMAT]
            hour_info = day_info['hours'][hour % TIME_FORMAT]
            new_row = [location, hour_info['datetime'], day_info['datetime']]

            # adding day info
            for column in DAY_COLUMNN_NAMES:
                new_row.append(day_info[column.replace('day_', '')])
            # adding hour info
            for column in HOUR_COLUMN_NAMES:
                new_row.append(hour_info[column.replace('hour_', '')])

            # adding region_id and is_weekend
            new_row.append(region_df.loc[region_df['center_city_en'] == location]['region_id'].iloc[0])
            new_row.append(datetime.datetime.strptime(day_info['datetime'], "%Y-%m-%d").isoweekday() in [6, 7])
            weather_df.loc[len(weather_df.index)] = new_row

    weather_df["hour_conditions"] = weather_df["hour_conditions"].astype('category').cat.codes
    weather_df["is_weekend"] = weather_df["is_weekend"].astype(int)
    weather_df.fillna(method="ffill")
    return weather_df


if __name__ == "__main__":
    print(get_weather())
