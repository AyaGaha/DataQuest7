"""
Model training module.

LightGBM pipeline optimized for Macro-F1 on 10-class imbalanced classification.
Features:
  - Rare class merging (8, 9 → 7) for training stability
  - Inverse sqrt sample weights for imbalance handling
  - StratifiedKFold 5-fold cross-validation
  - Early stopping per fold
  - Final model trained on full data at avg best iteration
"""

import os
import numpy as np
import pandas as pd
import lightgbm as lgb
import joblib
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import f1_score

from features import clean_data, split_features_target


def remap_rare_classes(y: pd.Series) -> pd.Series:
    """
    Merge ultra-rare classes into class 7 for training stability.
    Classes 8 and 9 each have only 5-6 samples — insufficient for learning.
    This only affects training labels; inference output is unchanged.
    """
    return y.replace({8: 7, 9: 7})


def compute_sample_weights(y: pd.Series) -> np.ndarray:
    """
    Compute per-sample weights using inverse square root of class frequency.
        weight_c = 1 / sqrt(count_c)
    Weights are normalized so the maximum weight is 1.
    """
    class_counts = y.value_counts()
    raw_weights = {cls: 1.0 / np.sqrt(count) for cls, count in class_counts.items()}
    max_w = max(raw_weights.values())
    normalized = {cls: w / max_w for cls, w in raw_weights.items()}
    return y.map(normalized).values


def get_lgb_params() -> dict:
    """Return regularized LightGBM params tuned for latency and Macro-F1."""
    return {
        'objective': 'multiclass',
        'num_class': 8,
        'n_estimators': 200,
        'learning_rate': 0.05,
        'num_leaves': 31,
        'max_depth': 6,
        'min_child_samples': 50,
        'subsample': 0.8,
        'subsample_freq': 1,
        'colsample_bytree': 0.8,
        'reg_alpha': 1.0,
        'reg_lambda': 1.0,
        'random_state': 42,
        'n_jobs': -1,
        'verbose': -1,
    }


def train_model(train_path: str, model_output_path: str = 'model.joblib') -> lgb.LGBMClassifier:
    """
    Train a LightGBM classifier with StratifiedKFold CV and save as model.joblib.

    Pipeline:
    1. Load and clean data
    2. Remap rare classes 8, 9 → 7 (training only)
    3. 5-fold stratified CV with early stopping to find stable best_iteration
    4. Train final model on full data at avg best_iteration + 10
    5. Save model.joblib
    """
    print("Loading training data...")
    df = pd.read_csv(train_path)
    print(f"Data shape: {df.shape}")

    print("\nCleaning data...")
    df_clean = clean_data(df)

    print("Splitting features and target...")
    X, y_original = split_features_target(df_clean)

    print("\nRemapping rare classes (8→7, 9→7)...")
    y = remap_rare_classes(y_original)

    print(f"Features shape: {X.shape}")
    print(f"\nOriginal target distribution:\n{y_original.value_counts().sort_index()}")
    print(f"\nRemapped target distribution:\n{y.value_counts().sort_index()}")

    cat_features = [c for c in X.columns if X[c].dtype.name == 'category']
    print(f"\nCategorical features ({len(cat_features)}): {cat_features}")
    print(f"Total features: {len(X.columns)}")

    print("\n" + "="*50)
    print("Starting 5-Fold Stratified Cross-Validation")
    print("="*50)

    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    fold_f1_scores = []
    best_iterations = []
    params = get_lgb_params()

    for fold, (train_idx, val_idx) in enumerate(skf.split(X, y), 1):
        X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]
        y_train, y_val = y.iloc[train_idx], y.iloc[val_idx]

        sample_weights = compute_sample_weights(y_train)

        model = lgb.LGBMClassifier(**params)
        model.fit(
            X_train, y_train,
            sample_weight=sample_weights,
            eval_set=[(X_val, y_val)],
            callbacks=[lgb.early_stopping(30, verbose=False)]
        )

        best_iterations.append(model.best_iteration_)
        y_pred = model.predict(X_val)
        macro_f1 = f1_score(y_val, y_pred, average='macro')
        fold_f1_scores.append(macro_f1)
        print(f"Fold {fold}: Macro-F1 = {macro_f1:.4f}  (best_iter = {model.best_iteration_})")

    mean_f1 = np.mean(fold_f1_scores)
    std_f1 = np.std(fold_f1_scores)
    avg_best_iter = int(np.mean(best_iterations)) + 10

    print(f"\n{'='*50}")
    print(f"CV Macro-F1 : {mean_f1:.4f} ± {std_f1:.4f}")
    print(f"Final n_estimators : {avg_best_iter}")
    print(f"{'='*50}")

    print("\nTraining final model on full data...")
    sample_weights_full = compute_sample_weights(y)
    cat_features_full = [c for c in X.columns if X[c].dtype.name == 'category']

    final_params = get_lgb_params()
    final_params['n_estimators'] = avg_best_iter

    final_model = lgb.LGBMClassifier(**final_params)
    final_model.fit(
        X, y,
        sample_weight=sample_weights_full,
        categorical_feature=cat_features_full
    )

    print(f"\nFinal model feature names ({len(final_model.feature_name_)}):\n{final_model.feature_name_}")

    # Save the trained model to the project root directory
    model_save_path = os.path.join(project_root, "model.joblib")
    joblib.dump(final_model, model_save_path)
    print(f"\nTrained model saved successfully to: {model_save_path}")

    return final_model


if __name__ == '__main__':
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)

    train_path = os.path.join(project_root, 'data', 'train.csv')
    model_path = os.path.join(project_root, 'model.joblib')

    print(f"Train path : {train_path}")
    print(f"Model path : {model_path}\n")

    train_model(train_path, model_path)

