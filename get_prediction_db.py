import pickle

from matrix import get_matrix
from weather import get_all_regions_list, TIME_FORMAT, PREDICTION_DURATION, get_start_hour_prediction
from datetime import date, timedelta
import pandas as pd

MODEL_FOLDER = "models/"
DATA_FOLDER = "data/"
SGD = "11__sgd__v2.pkl"
LOGISTIC_REGRESSION = "11__logistic_regression__v3.pkl"
SGD_CLASSIFIER = "11__sgd_classifier__v2.pkl"
model_path = f"{MODEL_FOLDER}{SGD_CLASSIFIER}"


def get_regions_id():
    region_df = pd.read_csv(f"{DATA_FOLDER}regions.csv")
    locations = list(region_df["center_city_en"].values)
    locations.remove("Simferopol")
    locations.remove("Luhansk")
    res = {}
    for region in locations:
        res[region] = region_df.loc[region_df['center_city_en'] == region]['region_id'].iloc[0]
    return res


def get_id_region():
    region_df = pd.read_csv(f"{DATA_FOLDER}regions.csv")
    locations = list(region_df["center_city_en"].values)
    locations.remove("Simferopol")
    locations.remove("Luhansk")
    res = {}
    for region in locations:
        res[region_df.loc[region_df['center_city_en'] == region]['region_id'].iloc[0]] = region
    return res


def get_prediction():
    with open(model_path, "rb") as file:
        model = pickle.load(file)

    matrix = get_matrix()
    predicted = list(model.predict(matrix))
    # print(predicted)

    response = []
    i = 0
    j = 0
    start_hour = get_start_hour_prediction()

    regions = get_all_regions_list()
    region_id = get_regions_id()

    for region in regions:

        for hour in range(start_hour, start_hour + PREDICTION_DURATION):
            alarm_date_start = (date.today() + timedelta(hour // TIME_FORMAT)).strftime("%Y-%m-%d")
            alarm_date_end = (date.today() + timedelta((hour + 1) // TIME_FORMAT)).strftime("%Y-%m-%d")
            response.append({"date_start": alarm_date_start + " " + str(hour % TIME_FORMAT) + ":00:00+02",
                             "date_end": alarm_date_end + " " + str((hour + 1) % TIME_FORMAT) + ":00:00+02",
                             "status": bool(predicted[i + j * PREDICTION_DURATION]),
                             "region_id": int(region_id[region])}
                            )
            i += 1
        i = 0
        j += 1

    return response


if __name__ == "__main__":
    print(get_prediction())
