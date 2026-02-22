"""
Feature engineering and data cleaning module.

This module provides functions for cleaning insurance policy data
and preparing it for model training and prediction.
"""

import pandas as pd
from typing import Tuple


# Define categorical columns that need to be converted to category dtype
CATEGORICAL_COLUMNS = [
    'Region_Code',
    'Broker_Agency_Type', 
    'Deductible_Tier',
    'Acquisition_Channel',
    'Payment_Schedule',
    'Employment_Status',
    'Policy_Start_Month'
]

TARGET_COLUMN = 'Purchased_Coverage_Bundle'


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and preprocess the input dataframe.
    
    This function performs the following operations:
    - Drops Employer_ID (94% missing)
    - Fills missing values for specific columns
    - Converts categorical columns to category dtype for LightGBM
    
    Args:
        df: Input pandas DataFrame with raw data
        
    Returns:
        Cleaned pandas DataFrame ready for modeling
    """
    df = df.copy()
    
    # Drop Employer_ID - 94% missing, not useful
    if 'Employer_ID' in df.columns:
        df = df.drop(columns=['Employer_ID'])
    
    # Fill missing values
    # Child_Dependents: fill with 0 (assumes no child dependents)
    if 'Child_Dependents' in df.columns:
        df['Child_Dependents'] = df['Child_Dependents'].fillna(0)
    
    # Region_Code: fill with "Unknown"
    if 'Region_Code' in df.columns:
        df['Region_Code'] = df['Region_Code'].fillna('Unknown')
    
    # Deductible_Tier: fill with "Unknown"
    if 'Deductible_Tier' in df.columns:
        df['Deductible_Tier'] = df['Deductible_Tier'].fillna('Unknown')
    
    # Acquisition_Channel: fill with "Unknown"
    if 'Acquisition_Channel' in df.columns:
        df['Acquisition_Channel'] = df['Acquisition_Channel'].fillna('Unknown')
    
    # Broker_ID: fill with -1 to indicate missing (numeric column)
    if 'Broker_ID' in df.columns:
        df['Broker_ID'] = df['Broker_ID'].fillna(-1)
    
    # Convert categorical columns to category dtype for LightGBM native handling
    for col in CATEGORICAL_COLUMNS:
        if col in df.columns:
            df[col] = df[col].astype('category')
    
    return df


def split_features_target(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
    """
    Split dataframe into features and target.
    
    Args:
        df: Cleaned pandas DataFrame containing both features and target
        
    Returns:
        Tuple of (X, y) where:
            - X: Feature DataFrame (excludes User_ID and target)
            - y: Target Series (Purchased_Coverage_Bundle)
    """
    # Columns to exclude from features
    exclude_cols = ['User_ID', TARGET_COLUMN]
    
    # Get feature columns
    feature_cols = [col for col in df.columns if col not in exclude_cols]
    
    X = df[feature_cols]
    y = df[TARGET_COLUMN]
    
    return X, y
