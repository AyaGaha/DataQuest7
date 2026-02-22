import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
from datetime import datetime

from solution import preprocess, load_model, predict

app = FastAPI(title="InsureAI Prediction API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:4173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load model once at startup
model = load_model()


class AssessmentInput(BaseModel):
    age: int = 35
    occupation: str = "employee"
    income: float = 75000
    maritalStatus: str = ""
    dependents: int = 0
    hasChildren: bool = False
    homeOwner: bool = False
    vehicles: int = 1
    propertyValue: float = 0
    currentInsurance: str = "none"
    claimsHistory: int = 0
    riskTolerance: str = "medium"


OCCUPATION_TO_EMPLOYMENT = {
    "professional": "Employed",
    "business": "Self-Employed",
    "employee": "Employed",
    "retired": "Retired",
    "self-employed": "Self-Employed",
}

RISK_TO_DEDUCTIBLE = {
    "low": "High",
    "medium": "Medium",
    "high": "Low",
}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/predict")
def predict_bundle(data: AssessmentInput):
    try:
        now = datetime.now()
        has_existing = data.currentInsurance not in ("", "none")

        # Split dependents into adult vs child
        child_deps = 1 if data.hasChildren else 0
        adult_deps = max(0, data.dependents - child_deps)

        row = {
            "User_ID": "U0001",
            "Policy_Cancelled_Post_Purchase": 0,
            "Policy_Start_Month": now.strftime("%b"),
            "Policy_Start_Year": now.year,
            "Policy_Start_Week": now.isocalendar()[1],
            "Policy_Start_Day": now.day,
            "Grace_Period_Extensions": 0,
            "Previous_Policy_Duration_Months": 12 if has_existing else 0,
            "Adult_Dependents": adult_deps,
            "Child_Dependents": child_deps,
            "Infant_Dependents": 0,
            "Existing_Policyholder": 1 if has_existing else 0,
            "Previous_Claims_Filed": data.claimsHistory,
            "Years_Without_Claims": max(0, 5 - data.claimsHistory),
            "Policy_Amendments_Count": 0,
            "Underwriting_Processing_Days": 5,
            "Vehicles_on_Policy": data.vehicles,
            "Custom_Riders_Requested": 0,
            "Broker_Agency_Type": "Direct",
            "Deductible_Tier": RISK_TO_DEDUCTIBLE.get(data.riskTolerance, "Medium"),
            "Acquisition_Channel": "Online",
            "Payment_Schedule": "Monthly",
            "Employment_Status": OCCUPATION_TO_EMPLOYMENT.get(data.occupation, "Employed"),
            "Estimated_Annual_Income": data.income,
            "Days_Since_Quote": 0,
        }

        df = pd.DataFrame([row])
        df_processed = preprocess(df)
        result = predict(model, df_processed)
        bundle_id = int(result["recommended_bundle"][0])

        return {"bundle_id": bundle_id}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))