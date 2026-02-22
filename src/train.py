"""
Model training module.

Optimized LightGBM pipeline for Macro-F1 on 10-class imbalanced classification.
Features:
  - Behavioral feature engineering
  - Log-inverse class weights for imbalance handling
  - Early stopping for compact model size
  - Compact booster export via text serialization
  - Feature importance artifacts for reporting
"""

import os
import numpy as np
import pandas as pd
import lightgbm as lgb
import joblib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score

from features import clean_data, split_features_target


def compute_class_weights(y: pd.Series) -> dict:
    """
    Compute class weights using inverse log frequency:
        weight_c = 1 / log(1.2 + freq_c)

    This gives more weight to rare classes without extreme scaling.
    """
    freq = y.value_counts(normalize=True)
    class_weight = {c: 1 / np.log(1.2 + freq[c]) for c in freq.index}
    return class_weight


def save_feature_importance(model: lgb.LGBMClassifier,
                             feature_names: list,
                             output_dir: str) -> None:
    """
    Save feature_importance.csv and top20_feature_plot.png.
    Not included in submission — for report only.
    """
    importances = model.feature_importances_
    fi_df = pd.DataFrame({
        'feature': feature_names,
        'importance': importances
    }).sort_values('importance', ascending=False).reset_index(drop=True)

    csv_path = os.path.join(output_dir, 'feature_importance.csv')
    fi_df.to_csv(csv_path, index=False)
    print(f"Feature importance saved to: {csv_path}")

    top20 = fi_df.head(20)
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.barh(top20['feature'][::-1], top20['importance'][::-1])
    ax.set_xlabel('Importance (split)')
    ax.set_title('Top 20 Feature Importances')
    plt.tight_layout()
    plot_path = os.path.join(output_dir, 'top20_feature_plot.png')
    fig.savefig(plot_path, dpi=120)
    plt.close(fig)
    print(f"Feature importance plot saved to: {plot_path}")


def train_model(train_path: str, model_output_path: str = 'model.joblib') -> lgb.LGBMClassifier:
    """
    Train an optimized LightGBM classifier and save as model.joblib.

    Pipeline:
    1. Load and clean data (includes behavioral feature engineering)
    2. Stratified train/validation split for early stopping
    3. Compute log-inverse class weights
    4. Train LGBMClassifier with early stopping
    5. Re-train compact final model with best_iteration_ on full data
    6. Save model.joblib + explainability artifacts
    """
    print("Loading training data...")
    df = pd.read_csv(train_path)
    print(f"Data shape: {df.shape}")

    print("\nCleaning and engineering features...")
    df_clean = clean_data(df)

    print("Splitting features and target...")
    X, y = split_features_target(df_clean)
    print(f"Features shape : {X.shape}")
    print(f"Target distribution:\n{y.value_counts().sort_index()}")

    # Stratified split for early stopping validation
    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=0.15, random_state=42, stratify=y
    )
    print(f"\nTrain: {len(X_train)}  |  Val: {len(X_val)}")

    cat_features = [c for c in X_train.columns if X_train[c].dtype.name == 'category']
    print(f"Categorical features ({len(cat_features)}): {cat_features}")

    # --- Class weights ---
    class_weight = compute_class_weights(y_train)
    print(f"\nClass weights:\n{ {k: round(v,4) for k, v in sorted(class_weight.items())} }")

    # --- Phase 1: find best_iteration_ with early stopping ---
    print("\n[Phase 1] Training with early stopping to find best iteration...")
    probe_model = lgb.LGBMClassifier(
        objective='multiclass',
        num_class=10,
        n_estimators=450,
        learning_rate=0.05,
        num_leaves=63,
        max_depth=8,
        min_child_samples=40,
        subsample=0.8,
        colsample_bytree=0.8,
        reg_alpha=0.2,
        reg_lambda=0.2,
        class_weight=class_weight,
        n_jobs=1,
        verbose=-1
    )

    probe_model.fit(
        X_train, y_train,
        eval_set=[(X_val, y_val)],
        eval_metric='multi_logloss',
        categorical_feature=cat_features,
        callbacks=[lgb.early_stopping(50, verbose=False)]
    )

    best_iter = probe_model.best_iteration_
    print(f"Best iteration: {best_iter}")

    # --- Evaluate probe model ---
    y_pred = probe_model.predict(X_val)
    acc = accuracy_score(y_val, y_pred)
    macro_f1 = f1_score(y_val, y_pred, average='macro')
    per_class_f1 = f1_score(y_val, y_pred, average=None, labels=sorted(y.unique()))
    print(f"\nValidation Accuracy : {acc:.4f}")
    print(f"Validation Macro-F1 : {macro_f1:.4f}")
    print("Per-class F1:")
    for cls, score in zip(sorted(y.unique()), per_class_f1):
        print(f"  Class {cls}: {score:.4f}")

    # --- Phase 2: compact final model on full data ---
    print(f"\n[Phase 2] Training compact final model on full data (n_estimators={best_iter})...")

    class_weight_full = compute_class_weights(y)
    cat_features_full = [c for c in X.columns if X[c].dtype.name == 'category']

    final_model = lgb.LGBMClassifier(
        objective='multiclass',
        num_class=10,
        n_estimators=best_iter,
        learning_rate=0.05,
        num_leaves=63,
        max_depth=8,
        min_child_samples=40,
        subsample=0.8,
        colsample_bytree=0.8,
        reg_alpha=0.2,
        reg_lambda=0.2,
        class_weight=class_weight_full,
        n_jobs=1,
        verbose=-1
    )

    final_model.fit(X, y, categorical_feature=cat_features_full)

    # --- Compact booster serialization ---
    print("\nSerializing compact booster via text format...")
    compact_txt = os.path.join(os.path.dirname(model_output_path), 'compact.txt')
    final_model.booster_.save_model(compact_txt, num_iteration=best_iter)

    # Reload into a fresh LGBMClassifier via the booster
    compact_booster = lgb.Booster(model_file=compact_txt)
    final_model._Booster = compact_booster
    print(f"Compact booster saved to: {compact_txt}")

    # --- Save model.joblib ---
    joblib.dump(final_model, model_output_path)
    print(f"\nmodel.joblib saved to: {model_output_path}")

    import os as _os
    size_mb = _os.path.getsize(model_output_path) / 1024**2
    print(f"Model size: {size_mb:.2f} MB")
    print(f"Features  : {len(final_model.feature_name_)}")
    print("Feature names:", final_model.feature_name_)

    # --- Explainability artifacts ---
    output_dir = os.path.dirname(model_output_path)
    save_feature_importance(final_model, final_model.feature_name_, output_dir)

    return final_model


if __name__ == '__main__':
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)

    train_path = os.path.join(project_root, 'data', 'train.csv')
    model_path = os.path.join(project_root, 'model.joblib')

    print(f"Train path : {train_path}")
    print(f"Model path : {model_path}\n")

    train_model(train_path, model_path)

