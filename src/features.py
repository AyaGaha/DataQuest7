"""
Feature engineering and data cleaning module.

This module provides functions for cleaning insurance policy data
and preparing it for model training and prediction.
"""

import pandas as pd
import numpy as np
from typing import Tuple


# Categorical columns after feature pruning (no Region_Code, Policy_Start_Month)
CATEGORICAL_COLUMNS = [
    'Broker_Agency_Type',
    'Deductible_Tier',
    'Acquisition_Channel',
    'Payment_Schedule',
    'Employment_Status'
]

TARGET_COLUMN = 'Purchased_Coverage_Bundle'

MONTH_MAP = {
    'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4,
    'May': 5, 'Jun': 6, 'Jul': 7, 'Aug': 8,
    'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
}


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and preprocess the input dataframe.

    Operations:
    - Drop Employer_ID, Broker_ID, Region_Code
    - Fill missing values
    - Cyclical encoding for Policy_Start_Month
    - Convert categorical columns to category dtype
    """
    df = df.copy()

    for col in ['Employer_ID', 'Broker_ID', 'Region_Code']:
        if col in df.columns:
            df = df.drop(columns=[col])

    if 'Child_Dependents' in df.columns:
        df['Child_Dependents'] = df['Child_Dependents'].fillna(0)

    if 'Deductible_Tier' in df.columns:
        df['Deductible_Tier'] = df['Deductible_Tier'].fillna('Unknown')

    if 'Acquisition_Channel' in df.columns:
        df['Acquisition_Channel'] = df['Acquisition_Channel'].fillna('Unknown')

    if 'Policy_Start_Month' in df.columns:
        month_num = df['Policy_Start_Month'].map(MONTH_MAP).fillna(1)
        df['month_sin'] = np.sin(2 * np.pi * month_num / 12)
        df['month_cos'] = np.cos(2 * np.pi * month_num / 12)
        df = df.drop(columns=['Policy_Start_Month'])

    for col in CATEGORICAL_COLUMNS:
        if col in df.columns:
            df[col] = df[col].astype('category')

    return df


def split_features_target(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
    """
    Split dataframe into features (X) and target (y).

    Excludes User_ID and Purchased_Coverage_Bundle from features.
    """
    exclude_cols = ['User_ID', TARGET_COLUMN]
    feature_cols = [col for col in df.columns if col not in exclude_cols]
    return df[feature_cols], df[TARGET_COLUMN]
