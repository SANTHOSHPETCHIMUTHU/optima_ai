"""
Enhanced Pydantic models for API requests/responses.
Mirrors optima-frontend's schema definitions for type safety.
"""

from pydantic import BaseModel
from typing import Optional, List, Dict, Any, Literal
from enum import Enum


# ── Experience Levels ──
class ExperienceLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    SENIOR = "senior"


class Purpose(str, Enum):
    CHAT = "chat"
    DIAGNOSE = "diagnose"
    CLEAN = "clean"


# ── User Profile ──
class UserProfile(BaseModel):
    name: Optional[str] = None
    level: ExperienceLevel
    purpose: Purpose
    role: Optional[str] = None


# ── Column Metadata ──
class ColumnMeta(BaseModel):
    name: str
    dtype: str
    null_count: int
    null_pct: float
    unique_count: int
    sample_values: List[Any]
    mean: Optional[float] = None
    std: Optional[float] = None
    min: Optional[Any] = None
    max: Optional[Any] = None


# ── Upload ──
class UploadResponse(BaseModel):
    file_id: str
    filename: str
    rows: int
    cols: int
    size_bytes: int
    columns: List[str]
    dtypes: Dict[str, str]
    message: Optional[str] = None


# ── Fingerprint / Analyze Init ──
class Fingerprint(BaseModel):
    file_id: str
    shape: tuple[int, int]
    columns: List[ColumnMeta]
    total_nulls: int
    null_pct_overall: float
    duplicate_rows: int
    redacted_sample: List[Dict[str, Any]]


# ── Diagnosis ──
class IssueSeverity(str, Enum):
    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"


class DiagnosisIssue(BaseModel):
    id: str
    column: Optional[str] = None
    severity: IssueSeverity
    title: str
    description: str
    affected_rows: Optional[int] = None
    affected_pct: Optional[float] = None
    fix_suggestion: Optional[str] = None


class ColumnProfile(BaseModel):
    column: str
    status: Literal["clean", "warning", "critical"]
    problems: List[str]


class DiagnosisResponse(BaseModel):
    file_id: str
    health_score: float  # 0-100
    summary: str
    issues: List[DiagnosisIssue]
    column_profiles: List[ColumnProfile]
    recommended_actions: List[str]
    full_report_md: str


# ── Chat ──
class ChatMessage(BaseModel):
    id: str
    role: Literal["user", "assistant"]
    content: str
    timestamp: int
    model: Optional[str] = None


class ChatRequest(BaseModel):
    file_id: Optional[str] = None
    messages: List[Dict[str, str]]
    model: str
    user_level: ExperienceLevel
    context: Optional[str] = None


class ChatResponse(BaseModel):
    id: str
    role: str
    content: str
    timestamp: int


# ── Cleaning ──
class CleaningAction(BaseModel):
    type: str
    params: Dict[str, Any]
    description: str
    affected_columns: Optional[List[str]] = None
    estimated_rows_affected: Optional[int] = None
    enabled: bool = True


class CleaningPlan(BaseModel):
    file_id: str
    actions: List[CleaningAction]
    estimated_duration_ms: Optional[int] = None


class ActionLogEntry(BaseModel):
    type: str
    params: Dict[str, Any]
    rows_before: int
    rows_after: int
    rows_affected: int
    cols_before: int
    cols_after: int
    duration_ms: int
    order_index: int
    description: str


class ColumnChange(BaseModel):
    column: str
    change_type: str
    details: str


class CleaningResult(BaseModel):
    file_id: str
    cleaned_file_id: str
    original_shape: tuple[int, int]
    cleaned_shape: tuple[int, int]
    rows_removed: int
    cols_removed: int
    nulls_before: int
    nulls_after: int
    duplicates_removed: int
    actions_log: List[ActionLogEntry]
    preview_original: List[Dict[str, Any]]
    preview_cleaned: List[Dict[str, Any]]
    column_changes: List[ColumnChange]


# ── Metrics ──
class MetricsResponse(BaseModel):
    task_type: Literal["classification", "regression"]
    target_column: str
    
    # Classification metrics
    accuracy_before: Optional[float] = None
    accuracy_after: Optional[float] = None
    f1_before: Optional[float] = None
    f1_after: Optional[float] = None
    precision_before: Optional[float] = None
    precision_after: Optional[float] = None
    recall_before: Optional[float] = None
    recall_after: Optional[float] = None
    
    # Regression metrics
    mae_before: Optional[float] = None
    mae_after: Optional[float] = None
    mse_before: Optional[float] = None
    mse_after: Optional[float] = None
    r2_before: Optional[float] = None
    r2_after: Optional[float] = None
    
    notes: Optional[str] = None


# ── Requests ──
class AnalyzeInitRequest(BaseModel):
    file_id: str


class AnalyzeRequest(BaseModel):
    file_id: str
    fingerprint: dict
    model: Optional[str] = None
    api_key: Optional[str] = None
    user_level: Optional[ExperienceLevel] = ExperienceLevel.BEGINNER


class DiagnoseRequest(BaseModel):
    file_id: str
    fingerprint: dict
    model: Optional[str] = None
    api_key: Optional[str] = None
    user_level: Optional[ExperienceLevel] = ExperienceLevel.BEGINNER


class CleanRequest(BaseModel):
    file_id: str
    fingerprint: dict
    model: Optional[str] = None
    api_key: Optional[str] = None
    user_level: Optional[ExperienceLevel] = ExperienceLevel.BEGINNER
    use_ai_plan: bool = True
    target_column: Optional[str] = None


class MetricsRequest(BaseModel):
    file_id: str
    cleaned_file_id: str
    target_column: str
    task_type: Literal["classification", "regression"]
