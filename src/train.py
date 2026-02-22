"""
Model training module.

This module provides functions for training a LightGBM classifier
on insurance policy data for multiclass classification.
"""

import pandas as pd
import numpy as np
import lightgbm as lgb
import joblib
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score

from features import clean_data, split_features_target, CATEGORICAL_COLUMNS


def train_model(train_path: str, model_output_path: str = 'model.joblib') -> lgb.LGBMClassifier:
    """
    Train a LightGBM classifier on the training data.
    
    This function:
    - Loads and cleans the training data
    - Performs stratified train/validation split
    - Trains LightGBM with balanced class weights
    - Evaluates on validation set
    - Saves the trained model
    
    Args:
        train_path: Path to the training CSV file
        model_output_path: Path where the model will be saved
        
    Returns:
        Trained LightGBM classifier
    """
    print("Loading training data...")
    df = pd.read_csv(train_path)
    print(f"Data shape: {df.shape}")
    
    print("\nCleaning data...")
    df_clean = clean_data(df)
    
    print("Splitting features and target...")
    X, y = split_features_target(df_clean)
    
    print(f"Features shape: {X.shape}")
    print(f"Target shape: {y.shape}")
    print(f"\nTarget distribution:\n{y.value_counts().sort_index()}")
    
    # Stratified train/validation split
    print("\nPerforming stratified train/validation split...")
    X_train, X_val, y_train, y_val = train_test_split(
        X, y, 
        test_size=0.2, 
        random_state=42, 
        stratify=y
    )
    print(f"Train size: {len(X_train)}, Validation size: {len(X_val)}")
    
    # Identify categorical features dynamically
    cat_features = [col for col in X_train.columns if X_train[col].dtype.name == 'category']
    print(f"\nCategorical features detected: {cat_features}")
    
    # Initialize LightGBM classifier
    print("\nInitializing LightGBM classifier...")
    model = lgb.LGBMClassifier(
        objective='multiclass',
        num_class=10,
        class_weight='balanced',
        n_estimators=500,
        learning_rate=0.05,
        max_depth=8,
        num_leaves=63,
        min_child_samples=20,
        subsample=0.8,
        colsample_bytree=0.8,
        reg_alpha=0.1,
        reg_lambda=0.1,
        random_state=42,
        n_jobs=-1,
        verbose=-1
    )
    
    # Train the model
    print("\nTraining model...")
    model.fit(
        X_train, 
        y_train,
        eval_set=[(X_val, y_val)],
        categorical_feature=cat_features
    )
    
    # Evaluate on validation set
    print("\nEvaluating on validation set...")
    y_pred = model.predict(X_val)
    
    accuracy = accuracy_score(y_val, y_pred)
    macro_f1 = f1_score(y_val, y_pred, average='macro')
    
    print(f"\n{'='*50}")
    print(f"Validation Accuracy: {accuracy:.4f}")
    print(f"Validation Macro F1: {macro_f1:.4f}")
    print(f"{'='*50}")
    
    # Print per-class F1 scores
    per_class_f1 = f1_score(y_val, y_pred, average=None)
    print("\nPer-class F1 scores:")
    for i, f1 in enumerate(per_class_f1):
        print(f"  Class {i}: {f1:.4f}")
    
    # Save the model
    print(f"\nSaving model to {model_output_path}...")
    joblib.dump(model, model_output_path)
    print("Model saved successfully!")
    
    return model


if __name__ == '__main__':
    # Train the model when script is run directly
    import os
    
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    
    train_path = os.path.join(project_root, 'data', 'train.csv')
    model_path = os.path.join(project_root, 'model.joblib')
    
    print(f"Training data path: {train_path}")
    print(f"Model output path: {model_path}")
    print()
    
    model = train_model(train_path, model_path)
