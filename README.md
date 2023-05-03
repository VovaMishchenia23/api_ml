# ALERTS PREDICTION
Alerts prediction is a program for forecasting air alerts for regions for the next 12 hours, which has a simple API interface

## Description
This project includes the following scripts:
- weather.py - collect weather data for the next 12 hours by region
- last_isw.py - get the latest isw report and present it as tf-idf matrix based on the previous 330 reports
- matrix.py - merge weather data and isw tf-idf matrix to one matrix for prediction
- get_prediction_db - predict alerts using trained ML model and matrix for prediction. Then collect this data in one dictionary for future insertion in db
- db_work.py - inserting new prediction data in db and getting data from db
- api.py - a simple API interface written in Flask with an endpoint for getting data about alerts prediction.

## API endpoints
- /prediction - endpoint for getting prediction for all regions or for the specific region if region value in the request body is not None

Example:

http://44.204.153.244:5000/prediction

region=Sumy

response body:
```
{
"last_prediciotn_time": "2023-04-24T16:26:33Z",
"last_model_train_time": "2023-05-03T10:52:47Z",
"regions_forecast": {
"Sumy": {
"2023-05-03 11:00:00": false,
"2023-05-03 12:00:00": false,
"2023-05-03 13:00:00": false,
"2023-05-03 14:00:00": false,
"2023-05-03 15:00:00": false,
"2023-05-03 16:00:00": false,
"2023-05-03 17:00:00": false,
"2023-05-03 18:00:00": false,
"2023-05-03 19:00:00": false,
"2023-05-03 20:00:00": false,
"2023-05-03 21:00:00": false,
"2023-05-03 22:00:00": false}
}
}
```
## ML model
The main ML model that we used for prediction alerts is SGDClassifier. SGD Classifier is a linear classifier (SVM, logistic regression, a.o.) optimized by the SGD. These are two different concepts. While SGD is an optimization method, Logistic Regression or linear Support Vector Machine is a machine learning algorithm/model.

Since our data had a large amplitude in values, we also used StandardScaler to standardize features by removing the mean and scaling to unit variance.

All the scripts for preparing data and training models you can find [here](https://github.com/VovaMishchenia23/prepare_dataset).

## Raliztion of frontend
Also, on the basis of this program, a frontend was created for user-friendly usage.

[Website link](https://air-alert-prediction-front-illidan04.vercel.app/)

[Frontend git project link](https://github.com/ILliDan04/air-alert-prediction-front)

