import joblib
from xmlrpc.client import Boolean
import uvicorn
import pandas as pd 
from pydantic import BaseModel
from typing import Literal, List
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
import json
from typing import Literal, List, Union

description = """"
Welcome to GETAROUND prediction API
GetAround is the Airbnb for cars. You can rent cars from any person for a few hours to a few days! Founded in 2009, this company has known rapid growth. In 2019, they count over 5 million users and about 20K available cars worldwide. 
GetAround is a company that allows car owners to rent their cars to customers.You just have to specify some informations about your car to make an approximation of what can be your rental price per day.

## Predict
* `/predict` put your cars informations here and you'll get you rental price per day.
"""

# tags to easily sort roots
tags_metadata = [
    {
        "name": "Prediction",
        "description": "Prediction of the rental price based on a machine learning model"
    }
]


# initialise API object
app = FastAPI(title="GETAROUND API",
    description=description,
    version="1.0",
    openapi_tags=tags_metadata)

    
# Define features used in machine learning
class PredictionFeatures(BaseModel):
    model_key: str = "Citroën"
    mileage: int = 140411
    engine_power: int = 100
    fuel: str = "diesel"
    paint_color: str = "black"
    car_type: str = "convertible"
    private_parking_available: bool = True
    has_gps: bool = True
    has_air_conditioning: bool = False
    automatic_car: bool = False
    has_getaround_connect: bool = True
    has_speed_regulator: bool = False
    winter_tires: bool = True



@app.post("/Prediction", tags=["Prediction"])
async def predict(predictionFeatures: PredictionFeatures):
    # Read data 
    df = pd.DataFrame(dict(predictionFeatures), index=[0])
    #print(df)

    # Load the models from local
    model_getaround  = 'model_1.joblib'
    regressor = joblib.load(model_getaround)
    prediction = regressor.predict(df)

    # Format response
    response = {"prediction": prediction.tolist()}
    return response

if __name__=="__main__":
    uvicorn.run(app, host="0.0.0.0", port=4000, debug=True, reload=True)

