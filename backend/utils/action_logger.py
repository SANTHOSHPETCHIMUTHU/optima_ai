"""
Enhanced Action Logging for Cleaning Operations
Tracks detailed metrics for each cleaning action.
"""

import time
import pandas as pd
from typing import Dict, List, Any, Optional
from datetime import datetime


class ActionLogger:
    """Logs cleaning actions with before/after metrics."""
    
    def __init__(self, df_original: pd.DataFrame):
        self.df_original = df_original.copy()
        self.df_current = df_original.copy()
        self.actions: List[Dict[str, Any]] = []
        self.action_index = 0
    
    def log_action(
        self,
        action_type: str,
        params: Dict[str, Any],
        description: str,
        affected_columns: Optional[List[str]] = None,
    ) -> None:
        """
        Log a cleaning action before and after its application.
        
        Args:
            action_type: Type of cleaning action
            params: Parameters passed to action
            description: Human-readable description
            affected_columns: Columns affected by this action
        """
        # Capture before state
        rows_before = len(self.df_current)
        cols_before = len(self.df_current.columns)
        
        # Time the action execution (placeholder - actual execution happens in caller)
        start_time = time.time()
        
        # Note: The actual dataframe modification happens in the caller
        # This method should be called AFTER the action is applied
        
        return {
            "action_type": action_type,
            "params": params,
            "description": description,
            "affected_columns": affected_columns,
        }
    
    def record_action_result(
        self,
        action_type: str,
        params: Dict[str, Any],
        description: str,
        affected_columns: Optional[List[str]] = None,
        start_time: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Record the result of a cleaning action.
        Call this AFTER the dataframe has been modified.
        
        Args:
            action_type: Type of cleaning action
            params: Parameters used
            description: Human-readable description
            affected_columns: Columns affected
            start_time: Start time from before the action
            
        Returns:
            Action log entry
        """
        # Current state (after action)
        rows_after = len(self.df_current)
        cols_after = len(self.df_current.columns)
        
        # Calculate duration
        end_time = time.time()
        duration_ms = int((end_time - (start_time or end_time)) * 1000)
        
        # Calculate affected rows
        rows_affected = rows_before = len(self.df_original)
        cols_before = len(self.df_original.columns)
        
        # Create log entry
        entry = {
            "type": action_type,
            "params": params,
            "rows_before": rows_before,
            "rows_after": rows_after,
            "rows_affected": abs(rows_before - rows_after),
            "cols_before": cols_before,
            "cols_after": cols_after,
            "duration_ms": duration_ms,
            "order_index": self.action_index,
            "description": description,
        }
        
        self.actions.append(entry)
        self.action_index += 1
        
        return entry
    
    def update_current_state(self, df: pd.DataFrame) -> None:
        """Update the current dataframe state for next action."""
        self.df_current = df.copy()
    
    def get_actions(self) -> List[Dict[str, Any]]:
        """Return all logged actions."""
        return self.actions.copy()
    
    def compute_column_changes(self, df_cleaned: pd.DataFrame) -> List[Dict[str, str]]:
        """
        Compute what changes happened to each column.
        
        Args:
            df_cleaned: The cleaned dataframe
            
        Returns:
            List of column change entries
        """
        changes = []
        
        # Check for removed columns
        for col in self.df_original.columns:
            if col not in df_cleaned.columns:
                changes.append({
                    "column": col,
                    "change_type": "removed",
                    "details": f"Column '{col}' was removed during cleaning",
                })
        
        # Check for new columns
        for col in df_cleaned.columns:
            if col not in self.df_original.columns:
                changes.append({
                    "column": col,
                    "change_type": "added",
                    "details": f"Column '{col}' was created during cleaning",
                })
        
        # Check for common columns
        for col in self.df_original.columns:
            if col in df_cleaned.columns:
                orig_nulls = self.df_original[col].isna().sum()
                clean_nulls = df_cleaned[col].isna().sum()
                
                if orig_nulls != clean_nulls:
                    changes.append({
                        "column": col,
                        "change_type": "nulls_reduced",
                        "details": f"Null values reduced from {orig_nulls} to {clean_nulls}",
                    })
                
                orig_dtype = str(self.df_original[col].dtype)
                clean_dtype = str(df_cleaned[col].dtype)
                
                if orig_dtype != clean_dtype:
                    changes.append({
                        "column": col,
                        "change_type": "dtype_changed",
                        "details": f"Data type changed from {orig_dtype} to {clean_dtype}",
                    })
        
        return changes


def compute_cleaning_summary(
    df_original: pd.DataFrame,
    df_cleaned: pd.DataFrame,
) -> Dict[str, Any]:
    """
    Compute summary statistics for the cleaning operation.
    
    Args:
        df_original: Original dataframe
        df_cleaned: Cleaned dataframe
        
    Returns:
        Summary dictionary
    """
    original_nulls = df_original.isna().sum().sum()
    cleaned_nulls = df_cleaned.isna().sum().sum()
    original_duplicates = df_original.duplicated().sum()
    cleaned_duplicates = df_cleaned.duplicated().sum()
    
    return {
        "original_shape": df_original.shape,
        "cleaned_shape": df_cleaned.shape,
        "rows_removed": len(df_original) - len(df_cleaned),
        "cols_removed": len(df_original.columns) - len(df_cleaned.columns),
        "nulls_before": int(original_nulls),
        "nulls_after": int(cleaned_nulls),
        "nulls_reduced": int(original_nulls - cleaned_nulls),
        "duplicates_before": int(original_duplicates),
        "duplicates_after": int(cleaned_duplicates),
        "duplicates_removed": int(original_duplicates - cleaned_duplicates),
    }
