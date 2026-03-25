import pandas as pd
import numpy as np
from typing import Dict, Any

def calculate_quality_metrics(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Calculates standard data quality metrics.
    For large datasets, metrics are calculated from a representative sample
    to ensure the application remains responsive.
    """
    total_rows = len(df)
    total_cols = len(df.columns)
    total_elements = df.size
    
    # Use a sample for metrics if the dataset is large
    is_sampled = total_rows > 50000
    df_metrics = df.sample(n=10000, random_state=42) if is_sampled else df
    sample_rows = len(df_metrics)
    sample_elements = df_metrics.size

    if total_elements == 0:
        return {
            "completeness": 0,
            "validity": 0,
            "consistency": 0,
            "uniqueness": 0,
            "accuracy": 0,
            "structural": 0
        }

    # 1. Completeness
    null_count = df_metrics.isnull().sum().sum()
    completeness = (sample_elements - null_count) / sample_elements if sample_elements > 0 else 0

    # 2. Validity
    validity_scores = []
    for col in df_metrics.columns:
        non_null_count = df_metrics[col].count()
        if non_null_count == 0:
            validity_scores.append(0)
            continue
        
        # Check if column is mostly one type
        type_counts = df_metrics[col].apply(type).value_counts()
        most_common_type_count = type_counts.iloc[0]
        validity_scores.append(most_common_type_count / non_null_count)
    validity = sum(validity_scores) / total_cols if total_cols > 0 else 0

    # 3. Consistency
    consistency = 1.0 - (df_metrics.isnull().any(axis=1).sum() / sample_rows * 0.2) if sample_rows > 0 else 1.0

    # 4. Uniqueness
    unique_rows = len(df_metrics.drop_duplicates())
    uniqueness = unique_rows / sample_rows if sample_rows > 0 else 0

    # 5. Accuracy
    numeric_cols = df_metrics.select_dtypes(include=[np.number]).columns
    if len(numeric_cols) > 0:
        outlier_total = 0
        for col in numeric_cols:
            q1 = df_metrics[col].quantile(0.25)
            q3 = df_metrics[col].quantile(0.75)
            iqr = q3 - q1
            outliers = df_metrics[(df_metrics[col] < (q1 - 1.5 * iqr)) | (df_metrics[col] > (q3 + 1.5 * iqr))]
            outlier_total += len(outliers)
        accuracy = 1.0 - (outlier_total / (sample_rows * len(numeric_cols)))
        accuracy = max(0.0, accuracy)
    else:
        accuracy = 1.0

    # 6. Structural
    valid_names = [c for c in df_metrics.columns if c and not str(c).startswith("Unnamed")]
    structural = len(valid_names) / total_cols if total_cols > 0 else 0

    return {
        "completeness": float(completeness),
        "validity": float(validity),
        "consistency": float(consistency),
        "uniqueness": float(uniqueness),
        "accuracy": float(accuracy),
        "structural": float(structural),
        "overall_score": float((completeness + validity + consistency + uniqueness + accuracy + structural) / 6),
        "is_sampled": is_sampled
    }
