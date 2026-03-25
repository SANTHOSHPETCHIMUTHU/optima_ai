import pandas as pd
import numpy as np
import re
from io import BytesIO

# --- Constants ---
PII_VALUE_EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", re.I)
PII_VALUE_PHONE = re.compile(r"\+?\d[\d\s\-()]{6,}\d")

def local_preprocess_fast(df: pd.DataFrame) -> pd.DataFrame:
    """
    Performs minimal preprocessing on load to ensure the app stays responsive.
    Only basic structure cleanup is done here. Aggressive cleaning (like stripping) 
    is deferred to the Clean execution stage.
    """
    # Drop rows/cols that are 100% empty - relatively fast
    df = df.dropna(how="all").dropna(axis=1, how="all")
    return df

def load_and_preprocess(file_name: str, file_bytes: bytes) -> pd.DataFrame:
    """
    Loads a CSV or Excel file from bytes and runs the initial fast preprocessing pass.
    """
    if file_name.endswith(".csv"):
        # Use low_memory=False to avoid DtypeWarnings on large files
        df = pd.read_csv(BytesIO(file_bytes), low_memory=False)
    else:
        df = pd.read_excel(BytesIO(file_bytes), engine="openpyxl")
    return local_preprocess_fast(df)

def dataset_fingerprint(df: pd.DataFrame, sample_rows: int = 10, max_cat_cols: int = 30) -> dict:
    """
    Generates a secure, statistical fingerprint of the dataset.
    For large datasets (>50k rows), statistics are calculated from a representative sample
    to ensure the UI remains responsive. Shape and columns are always accurate.
    """
    total_rows = len(df)
    is_sampled = total_rows > 50000
    
    # Use a sample for expensive stats if the dataset is massive
    df_stats = df.sample(n=10000, random_state=42) if is_sampled else df
    
    shape = df.shape
    dtypes = df.dtypes.astype(str).to_dict()
    
    # Null percentage and nunique are fast but can add up on huge files
    null_pct = (df_stats.isna().mean() * 100).round(2).to_dict()
    nunique = df_stats.nunique(dropna=True).to_dict()

    # Vectorized numeric stats
    num_cols = df.select_dtypes(include=np.number).columns
    num_stats = {}
    if not num_cols.empty:
        # agg(['median', 'std']) is the slow part on huge data
        num_stats = df_stats[num_cols].agg(["min", "max", "mean", "median", "std"]).round(4).to_dict()

    # Create a safe sample with PII masked (head only)
    sample = df.head(sample_rows).copy()
    obj_cols = df.select_dtypes(include=["object", "string"]).columns[:max_cat_cols]
    
    for c in obj_cols:
        if c in sample.columns:
            s = sample[c].astype(str)
            s = s.str.replace(PII_VALUE_EMAIL, "[REDACTED_EMAIL]", regex=True)
            s = s.str.replace(PII_VALUE_PHONE, "[REDACTED_PHONE]", regex=True)
            sample[c] = s

    # Generate a safe human-readable summary
    safe_summary = f"Dataset with {shape[0]} rows and {shape[1]} columns. "
    if is_sampled:
        safe_summary += "(Statistics based on 10k row sample). "
    safe_summary += f"Columns: {', '.join(df.columns)}. "
    safe_summary += f"Data quality: {round(df_stats.notna().mean().mean() * 100, 1)}% complete."

    return {
        "shape": shape,
        "is_sampled": is_sampled,
        "columns": list(df.columns),
        "dtypes": dtypes,
        "null_pct": null_pct,
        "nunique": nunique,
        "numeric_stats": num_stats,
        "safe_sample": sample.to_dict(orient="records"),
        "safe_summary": safe_summary
    }
