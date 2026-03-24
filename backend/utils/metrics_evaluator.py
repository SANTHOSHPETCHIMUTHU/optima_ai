"""
Metrics Evaluation Module
Computes classification and regression metrics before/after cleaning.
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional, Tuple, Literal
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    mean_absolute_error, mean_squared_error, r2_score
)


def _prepare_data(df: pd.DataFrame, target_column: str) -> Tuple[np.ndarray, np.ndarray, Optional[np.ndarray]]:
    """
    Prepare features and target for ML evaluation.
    Handles missing values and categorical encoding.
    
    Returns:
        X: Feature matrix
        y: Target variable
        encoder: LabelEncoder if classification (for inverse transform), else None
    """
    if target_column not in df.columns:
        raise ValueError(f"Target column '{target_column}' not found in dataset")
    
    # Extract target
    y = df[target_column].copy()
    
    # Remove rows with missing target
    valid_idx = ~y.isna()
    y = y[valid_idx]
    
    # Extract features (all columns except target)
    X = df.loc[valid_idx, df.columns != target_column].copy()
    
    # Handle categorical columns
    le_dict = {}
    for col in X.select_dtypes(include=['object']).columns:
        le = LabelEncoder()
        X[col] = le.fit_transform(X[col].astype(str))
        le_dict[col] = le
    
    # Fill numeric NaNs with median
    for col in X.select_dtypes(include=[np.number]).columns:
        X[col].fillna(X[col].median(), inplace=True)
    
    # Encode target if it's categorical
    encoder = None
    if y.dtype == 'object' or str(y.dtype) == 'category':
        encoder = LabelEncoder()
        y_encoded = encoder.fit_transform(y.astype(str))
    else:
        y_encoded = y.values
    
    return X.values, y_encoded, encoder


def evaluate_classification(
    df_before: pd.DataFrame,
    df_after: pd.DataFrame,
    target_column: str
) -> Dict[str, Optional[float]]:
    """
    Evaluate classification performance before and after cleaning.
    
    Returns:
        Dict with accuracy, precision, recall, f1 for both before and after
    """
    results = {
        "accuracy_before": None,
        "accuracy_after": None,
        "precision_before": None,
        "precision_after": None,
        "recall_before": None,
        "recall_after": None,
        "f1_before": None,
        "f1_after": None,
    }
    
    try:
        # Before cleaning
        X_before, y_before, _ = _prepare_data(df_before, target_column)
        if len(X_before) > 10 and len(np.unique(y_before)) > 1:
            X_train, X_test, y_train, y_test = train_test_split(
                X_before, y_before, test_size=0.2, random_state=42
            )
            clf = RandomForestClassifier(n_estimators=50, random_state=42, max_depth=10)
            clf.fit(X_train, y_train)
            y_pred = clf.predict(X_test)
            
            results["accuracy_before"] = float(accuracy_score(y_test, y_pred))
            results["precision_before"] = float(precision_score(y_test, y_pred, average='weighted', zero_division=0))
            results["recall_before"] = float(recall_score(y_test, y_pred, average='weighted', zero_division=0))
            results["f1_before"] = float(f1_score(y_test, y_pred, average='weighted', zero_division=0))
    except Exception as e:
        print(f"Warning: Classification evaluation before failed: {e}")
    
    try:
        # After cleaning
        X_after, y_after, _ = _prepare_data(df_after, target_column)
        if len(X_after) > 10 and len(np.unique(y_after)) > 1:
            X_train, X_test, y_train, y_test = train_test_split(
                X_after, y_after, test_size=0.2, random_state=42
            )
            clf = RandomForestClassifier(n_estimators=50, random_state=42, max_depth=10)
            clf.fit(X_train, y_train)
            y_pred = clf.predict(X_test)
            
            results["accuracy_after"] = float(accuracy_score(y_test, y_pred))
            results["precision_after"] = float(precision_score(y_test, y_pred, average='weighted', zero_division=0))
            results["recall_after"] = float(recall_score(y_test, y_pred, average='weighted', zero_division=0))
            results["f1_after"] = float(f1_score(y_test, y_pred, average='weighted', zero_division=0))
    except Exception as e:
        print(f"Warning: Classification evaluation after failed: {e}")
    
    return results


def evaluate_regression(
    df_before: pd.DataFrame,
    df_after: pd.DataFrame,
    target_column: str
) -> Dict[str, Optional[float]]:
    """
    Evaluate regression performance before and after cleaning.
    
    Returns:
        Dict with MAE, MSE, R² for both before and after
    """
    results = {
        "mae_before": None,
        "mae_after": None,
        "mse_before": None,
        "mse_after": None,
        "r2_before": None,
        "r2_after": None,
    }
    
    try:
        # Before cleaning
        X_before, y_before, _ = _prepare_data(df_before, target_column)
        if len(X_before) > 10 and np.std(y_before) > 0:
            X_train, X_test, y_train, y_test = train_test_split(
                X_before, y_before, test_size=0.2, random_state=42
            )
            reg = RandomForestRegressor(n_estimators=50, random_state=42, max_depth=10)
            reg.fit(X_train, y_train)
            y_pred = reg.predict(X_test)
            
            results["mae_before"] = float(mean_absolute_error(y_test, y_pred))
            results["mse_before"] = float(mean_squared_error(y_test, y_pred))
            results["r2_before"] = float(r2_score(y_test, y_pred))
    except Exception as e:
        print(f"Warning: Regression evaluation before failed: {e}")
    
    try:
        # After cleaning
        X_after, y_after, _ = _prepare_data(df_after, target_column)
        if len(X_after) > 10 and np.std(y_after) > 0:
            X_train, X_test, y_train, y_test = train_test_split(
                X_after, y_after, test_size=0.2, random_state=42
            )
            reg = RandomForestRegressor(n_estimators=50, random_state=42, max_depth=10)
            reg.fit(X_train, y_train)
            y_pred = reg.predict(X_test)
            
            results["mae_after"] = float(mean_absolute_error(y_test, y_pred))
            results["mse_after"] = float(mean_squared_error(y_test, y_pred))
            results["r2_after"] = float(r2_score(y_test, y_pred))
    except Exception as e:
        print(f"Warning: Regression evaluation after failed: {e}")
    
    return results


def evaluate_metrics(
    df_before: pd.DataFrame,
    df_after: pd.DataFrame,
    target_column: str,
    task_type: Literal["classification", "regression"]
) -> Dict[str, Optional[float]]:
    """
    Evaluate model performance before and after cleaning.
    
    Args:
        df_before: Original dataframe
        df_after: Cleaned dataframe
        target_column: Target variable column name
        task_type: "classification" or "regression"
        
    Returns:
        Dictionary of metrics
    """
    if task_type == "classification":
        return evaluate_classification(df_before, df_after, target_column)
    elif task_type == "regression":
        return evaluate_regression(df_before, df_after, target_column)
    else:
        raise ValueError(f"Unknown task_type: {task_type}")
