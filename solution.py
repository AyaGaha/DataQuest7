# ----------------------------------------------------------------
# IMPORTANT: This template will be used to evaluate your solution.
#
# Do NOT change the function signatures.
# And ensure that your code runs within the time limits.
# The time calculation will be computed for the predict function only.
#
# Good luck!
# ----------------------------------------------------------------


# Import necessary libraries here
import pandas as pd
import joblib
from src.features import clean_data


def preprocess(df):
    """
    Preprocess the input dataframe for prediction.
    
    This function:
    - Calls clean_data to handle missing values and categorical encoding
    - Drops target column if present (for training data passed during inference)
    - Keeps User_ID for final prediction output
    
    Args:
        df: Raw input pandas DataFrame
        
    Returns:
        Preprocessed pandas DataFrame ready for model inference
    """
    # Clean the data using the shared cleaning function
    df_clean = clean_data(df)
    
    # Drop target column if it exists (handles case where train data is passed)
    if 'Purchased_Coverage_Bundle' in df_clean.columns:
        df_clean = df_clean.drop(columns=['Purchased_Coverage_Bundle'])
    
    return df_clean


def load_model():
    """
    Load the trained model from disk.
    
    Returns:
        Trained LightGBM model object
    """
    model = joblib.load('model.joblib')
    return model


def predict(df, model):
    """
    Generate predictions using the trained model.
    
    Args:
        df: Preprocessed pandas DataFrame (output of preprocess function)
        model: Trained model object (output of load_model function)
        
    Returns:
        pandas DataFrame with exactly two columns:
            - User_ID: User identifier
            - Purchased_Coverage_Bundle: Predicted class (int, 0-9)
    """
    # Extract User_ID before dropping for prediction
    user_ids = df['User_ID'].copy()
    
    # Get feature columns (exclude User_ID)
    feature_cols = [col for col in df.columns if col != 'User_ID']
    X = df[feature_cols]
    
    # Generate predictions
    preds = model.predict(X)
    
    # Create output DataFrame with required columns
    predictions = pd.DataFrame({
        'User_ID': user_ids,
        'Purchased_Coverage_Bundle': preds.astype(int)
    })
    
    return predictions


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
