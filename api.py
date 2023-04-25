import json
import pickle
import sqlalchemy
import pytz
from flask import Flask, request, jsonify
from db_work import get_data, insert_data_db, DATA_FOLDER, LAST_TIME_PREDICTION_FILE
from get_prediction_db import model_path
from datetime import datetime
import pathlib
from get_prediction_db import get_id_region, get_regions_id
from apscheduler.schedulers.background import BackgroundScheduler
import sqlalchemy as db
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

API_TOKEN = os.getenv("API_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")
PORT = os.getenv("PORT")

# db connection
engine = db.create_engine(DATABASE_URL, isolation_level="SERIALIZABLE")
connection = engine.connect()

# schedule jobs
scheduler = BackgroundScheduler()
scheduler.add_job(func=insert_data_db, trigger="interval", minutes=5, args=[connection, engine])
scheduler.start()


def get_prediction(region="all"):
    if region == "all":
        predictions = get_data(connection, engine)
    else:
        region_id = get_regions_id()
        predictions = get_data(connection, engine, region_id=int(region_id[region]))

    with open(f"{DATA_FOLDER}{LAST_TIME_PREDICTION_FILE}", "rb") as file:
        last_prediction_time = pickle.load(file)
    response = {"last_prediciotn_time": last_prediction_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "last_model_train_time": datetime.fromtimestamp(pathlib.Path(model_path).stat().st_mtime).strftime(
                    "%Y-%m-%dT%H:%M:%SZ"),
                "regions_forecast": {}}
    id_region = get_id_region()

    for value in predictions:
        region = id_region[value[4]]
        if region not in response["regions_forecast"]:
            response["regions_forecast"][region] = {}
        response["regions_forecast"][region][
            value[1].astimezone(pytz.timezone('Europe/Berlin')).strftime("%Y-%m-%d %H:%M:%S")] = value[3]

    return response


class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv["message"] = self.message
        return rv


@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@app.route("/")
def home_page():
    return "<p>Weather API</p>"


@app.route(
    "/prediction"
)
def weather_endpoint():
    token = request.form.get("token")

    if token is None:
        raise InvalidUsage("token is required", status_code=400)

    if token != API_TOKEN:
        raise InvalidUsage(f"wrong API token {token}", status_code=403)

    region = request.form.get("region")
    try:
        if region is None:
            result = json.dumps(get_prediction(), indent=4)
        elif region not in list(get_regions_id().keys()):
            raise InvalidUsage(f"Incorrect name of region", status_code=400)
        else:
            result = json.dumps(get_prediction(region), indent=4)
    except sqlalchemy.exc.OperationalError:
        raise InvalidUsage(f"server is busy", status_code=503)

    return result


if __name__ == '__main__':
    app.run(port=PORT)
