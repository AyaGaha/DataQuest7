# ----------------------------------------------------------------
# IMPORTANT: This template will be used to evaluate your solution.
#
# Do NOT change the function signatures.
# And ensure that your code runs within the time limits.
# The time calculation will be computed for the predict function only.
#
# Good luck!
# ----------------------------------------------------------------


import pandas as pd
import numpy as np
import joblib


FEATURE_COLUMNS = [
    'Policy_Cancelled_Post_Purchase',
    'Policy_Start_Year',
    'Policy_Start_Week',
    'Policy_Start_Day',
    'Grace_Period_Extensions',
    'Previous_Policy_Duration_Months',
    'Adult_Dependents',
    'Child_Dependents',
    'Infant_Dependents',
    'Existing_Policyholder',
    'Previous_Claims_Filed',
    'Years_Without_Claims',
    'Policy_Amendments_Count',
    'Underwriting_Processing_Days',
    'Vehicles_on_Policy',
    'Custom_Riders_Requested',
    'Broker_Agency_Type',
    'Deductible_Tier',
    'Acquisition_Channel',
    'Payment_Schedule',
    'Employment_Status',
    'Estimated_Annual_Income',
    'Days_Since_Quote',
    'month_sin',
    'month_cos',
    'Family_Size',
    'Risk_Index',
    'Policy_Engagement',
    'Time_To_Convert',
    'Income_Per_Dependent',
    'Loyalty_Score'
]

CATEGORICAL_COLUMNS = [
    'Broker_Agency_Type',
    'Deductible_Tier',
    'Acquisition_Channel',
    'Payment_Schedule',
    'Employment_Status'
]

MONTH_MAP = {
    'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4,
    'May': 5, 'Jun': 6, 'Jul': 7, 'Aug': 8,
    'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
}


def preprocess(df):
    df = df.copy()

    for col in ['Employer_ID', 'Broker_ID', 'Region_Code']:
        if col in df.columns:
            df = df.drop(columns=[col])

    if 'Purchased_Coverage_Bundle' in df.columns:
        df = df.drop(columns=['Purchased_Coverage_Bundle'])

    df['Child_Dependents'] = df['Child_Dependents'].fillna(0)
    df['Deductible_Tier'] = df['Deductible_Tier'].fillna('Unknown')
    df['Acquisition_Channel'] = df['Acquisition_Channel'].fillna('Unknown')

    if 'Policy_Start_Month' in df.columns:
        month_num = df['Policy_Start_Month'].map(MONTH_MAP).fillna(1)
        df['month_sin'] = np.sin(2 * np.pi * month_num / 12)
        df['month_cos'] = np.cos(2 * np.pi * month_num / 12)
        df = df.drop(columns=['Policy_Start_Month'])

    for col in CATEGORICAL_COLUMNS:
        if col in df.columns:
            df[col] = df[col].astype('category')

    # Behavioral feature engineering
    df['Family_Size'] = (
        df['Adult_Dependents'] + df['Child_Dependents'] + df['Infant_Dependents']
    )
    df['Risk_Index'] = (
        df['Previous_Claims_Filed'] / (df['Years_Without_Claims'] + 1)
    )
    df['Policy_Engagement'] = (
        df['Policy_Amendments_Count'] + df['Custom_Riders_Requested']
    )
    df['Time_To_Convert'] = (
        df['Days_Since_Quote'] / (df['Underwriting_Processing_Days'] + 1)
    )
    df['Income_Per_Dependent'] = (
        df['Estimated_Annual_Income'] / (df['Family_Size'] + 1)
    )
    df['Loyalty_Score'] = (
        df['Existing_Policyholder'] * df['Years_Without_Claims']
    )

    return df


def load_model():
    return joblib.load('model.joblib')


def predict(df, model):
    user_ids = df['User_ID'].copy()
    
    X = df[FEATURE_COLUMNS]
    
    preds = model.predict(X)
    
    return pd.DataFrame({
        'User_ID': user_ids,
        'Purchased_Coverage_Bundle': preds.astype(int)
    })


# ----------------------------------------------------------------
# Your code will be called in the following way:
# Note that we will not be using the function defined below.
# ----------------------------------------------------------------


def run(df) -> tuple[float, float, float]:
    from time import time

    # Load the processed data:
    df_processed = preprocess(df)

    # Load the model:
    model = load_model()
    size = get_model_size(model)

    # Get the predictions and time taken:
    start = time.perf_counter()
    predictions = predict(
        df_processed, model
    )  # NOTE: Don't call the `preprocess` function here.

    duration = time.perf_counter() - start
    accuracy = get_model_accuracy(predictions)

    return size, accuracy, duration


# ----------------------------------------------------------------
# Helper functions you should not disturb yourself with.
# ----------------------------------------------------------------


def get_model_size(model):
    pass


def get_model_accuracy(predictions):
    pass
