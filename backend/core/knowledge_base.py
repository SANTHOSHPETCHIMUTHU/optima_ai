import json
import os
import uuid
from typing import List, Dict, Any, Optional

class KnowledgeBase:
    """
    Manages the persistent storage and retrieval of cleaning patterns.
    Patterns are categorized as 'staged' (awaiting review) or 'verified' (ready for use).
    """
    
    def __init__(self, db_path: str = "backend/data/patterns.json"):
        # Adjust path if relative
        if not os.path.isabs(db_path):
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.db_path = os.path.join(base_dir, "data", "patterns.json")
        else:
            self.db_path = db_path
            
        self.data = self._load()

    def _load(self) -> Dict[str, List[Dict]]:
        if not os.path.exists(self.db_path):
            return {"verified_patterns": [], "staged_patterns": []}
        try:
            with open(self.db_path, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {"verified_patterns": [], "staged_patterns": []}

    def _save(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        with open(self.db_path, "w") as f:
            json.dump(self.data, f, indent=2)

    def find_matching_fix(self, fingerprint: Dict[str, Any]) -> Optional[Dict]:
        """
        Attempts to find a verified fix that matches the given dataset fingerprint.
        Matching is currently based on column name intersection and data type similarity.
        """
        verified = self.data.get("verified_patterns", [])
        
        # Simple matching for now: focus on column names
        current_cols = set(fingerprint.get("columns", []))
        
        for p in verified:
            pattern_cols = set(p.get("columns", []))
            # If 80% of columns match, consider it a potential candidate
            if pattern_cols and pattern_cols.issubset(current_cols):
                return p
        return None

    def stage_pattern(self, columns: List[str], fix_code: str, description: str, source_file: str) -> str:
        """Adds a new pattern to the staging area for human review."""
        new_id = str(uuid.uuid4()).split('-')[0]
        new_pattern = {
            "id": new_id,
            "columns": columns,
            "fix_code": fix_code,
            "description": description,
            "source_file": source_file,
            "is_verified": False
        }
        self.data["staged_patterns"].append(new_pattern)
        self._save()
        return new_id

    def verify_pattern(self, pattern_id: str) -> bool:
        """Promotes a pattern from staged to verified."""
        staged = self.data.get("staged_patterns", [])
        for i, p in enumerate(staged):
            if p["id"] == pattern_id:
                p["is_verified"] = True
                self.data["verified_patterns"].append(p)
                staged.pop(i)
                self._save()
                return True
        return False

    def get_all_patterns(self) -> Dict[str, List[Dict]]:
        return self.data

# Singleton instance
kb = KnowledgeBase()
