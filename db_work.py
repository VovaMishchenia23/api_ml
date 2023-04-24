import datetime
import pickle

import sqlalchemy
import sqlalchemy as db
from get_prediction_db import get_prediction

DATA_FOLDER = "data/"
LAST_TIME_PREDICTION_FILE = "last_time_prediction.pkl"


def insert_data_db(connection, engine):
    with open("logger.txt", "a") as file:
        file.write(f"{datetime.datetime.now().strftime('%H:%M:%S')}: Inserting in db...\n")
    try:
        metadata = db.MetaData()
        predictions_table = db.Table('predictions', metadata, autoload_with=engine)

        values = get_prediction()
        with open(f"{DATA_FOLDER}{LAST_TIME_PREDICTION_FILE}", "wb") as file:
            pickle.dump(datetime.datetime.now(), file)
        query = db.delete(predictions_table)
        result_proxy = connection.execute(query)
        print("Deleting data: ", result_proxy)
        query = db.insert(predictions_table)
        result_proxy = connection.execute(query, values)
        print("Inserting new data: ", result_proxy)
        connection.commit()
        with open("logger.txt", "a") as file:
            file.write(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: New data was inserted successfully\n")
    except sqlalchemy.exc.OperationalError:
        with open("logger.txt", "a") as file:
            file.write(
                f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: Fail inserting new data in db: too many connections fo role\n")


def get_data(connection, engine, region_id=None):
    metadata = db.MetaData()
    predictions_table = db.Table('predictions', metadata, autoload_with=engine)
    if region_id is None:
        query = db.select(predictions_table)
    else:
        query = db.select(predictions_table).where(predictions_table.columns.region_id == region_id)
    result_proxy = connection.execute(query)

    result_set = result_proxy.fetchall()
    return result_set

# if __name__ == "__main__":
#     insert_data_db()
#     print(get_data())
