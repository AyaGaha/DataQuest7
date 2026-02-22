import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from fastapi import FastAPI
import pandas as pd

# import your ML functions
from solution import preprocess, load_model, predict

app = FastAPI()

# load model once when server starts
model = load_model()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/predict")
def predict_customer(data: dict):
    # JSON -> dataframe
    df = pd.DataFrame([data])

    # preprocess
    df_processed = preprocess(df)

    # predict
    pred = predict(model, df_processed)

    return {"recommended_bundle": int(pred[0])}