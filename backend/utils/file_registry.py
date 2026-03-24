"""
File Registry: Maps file IDs to local file paths.
Persists registration in JSON for recovery across restarts.
"""

import os
import json
import uuid
from datetime import datetime
from typing import Optional, Dict

REGISTRY_FILE = os.path.join(os.path.dirname(__file__), "file_registry.json")


class FileRegistry:
    """Manages file ID to file path mappings."""
    
    def __init__(self):
        self.registry: Dict[str, Dict] = {}
        self._load_registry()
    
    def _load_registry(self):
        """Load registry from disk if it exists."""
        if os.path.exists(REGISTRY_FILE):
            try:
                with open(REGISTRY_FILE, "r") as f:
                    self.registry = json.load(f)
            except Exception as e:
                print(f"Warning: Failed to load registry: {e}")
                self.registry = {}
    
    def _save_registry(self):
        """Persist registry to disk."""
        try:
            with open(REGISTRY_FILE, "w") as f:
                json.dump(self.registry, f, indent=2)
        except Exception as e:
            print(f"Warning: Failed to save registry: {e}")
    
    def register(self, file_path: str, filename: str) -> str:
        """
        Register a file and return its file_id.
        
        Args:
            file_path: Full local path to the file
            filename: Original filename for reference
            
        Returns:
            file_id: Unique identifier for this file
        """
        file_id = str(uuid.uuid4())
        self.registry[file_id] = {
            "file_path": file_path,
            "filename": filename,
            "registered_at": datetime.utcnow().isoformat(),
            "size_bytes": os.path.getsize(file_path) if os.path.exists(file_path) else 0,
        }
        self._save_registry()
        return file_id
    
    def get_path(self, file_id: str) -> Optional[str]:
        """Get the file path for a given file_id."""
        if file_id in self.registry:
            return self.registry[file_id]["file_path"]
        return None
    
    def get_metadata(self, file_id: str) -> Optional[Dict]:
        """Get all metadata for a file_id."""
        if file_id in self.registry:
            return self.registry[file_id].copy()
        return None
    
    def register_cleaned(self, original_file_id: str, cleaned_file_path: str) -> str:
        """
        Register a cleaned version of an existing file.
        
        Args:
            original_file_id: The original file's ID
            cleaned_file_path: Path to the cleaned file
            
        Returns:
            cleaned_file_id: New ID for the cleaned file
        """
        if original_file_id not in self.registry:
            raise ValueError(f"Original file_id {original_file_id} not found")
        
        original_meta = self.registry[original_file_id]
        original_filename = original_meta["filename"]
        base_name = os.path.splitext(original_filename)[0]
        cleaned_filename = f"{base_name}_cleaned.csv"
        
        cleaned_file_id = str(uuid.uuid4())
        self.registry[cleaned_file_id] = {
            "file_path": cleaned_file_path,
            "filename": cleaned_filename,
            "registered_at": datetime.utcnow().isoformat(),
            "size_bytes": os.path.getsize(cleaned_file_path) if os.path.exists(cleaned_file_path) else 0,
            "original_file_id": original_file_id,
            "is_cleaned": True,
        }
        self._save_registry()
        return cleaned_file_id
    
    def list_all(self) -> Dict[str, Dict]:
        """Return all registered files."""
        return self.registry.copy()
    
    def delete(self, file_id: str) -> bool:
        """Remove a file from registry (doesn't delete the actual file)."""
        if file_id in self.registry:
            del self.registry[file_id]
            self._save_registry()
            return True
        return False


# Global instance
_registry = FileRegistry()


def register_file(file_path: str, filename: str) -> str:
    """Register a file and return its ID."""
    return _registry.register(file_path, filename)


def get_file_path(file_id: str) -> Optional[str]:
    """Get file path from ID."""
    return _registry.get_path(file_id)


def get_file_metadata(file_id: str) -> Optional[Dict]:
    """Get file metadata from ID."""
    return _registry.get_metadata(file_id)


def register_cleaned_file(original_file_id: str, cleaned_file_path: str) -> str:
    """Register a cleaned file."""
    return _registry.register_cleaned(original_file_id, cleaned_file_path)
