"""
file_manager.py - Handles JSON persistence for Resume Builder.

FileManager.save_data()  - serialises a Resume to a JSON file in data/
FileManager.load_data()  - deserialises a JSON file back into a Resume
FileManager.list_saved() - returns a sorted list of saved resume filenames
"""

import json
import os
from pathlib import Path
from models import Resume


# Where we store JSON files (relative to this script's location)
DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)


class FileManager:
    """
    Manages reading and writing Resume data to/from JSON files.

    All files are stored under the  data/  directory as  <name>.json.
    """

    @staticmethod
    def _safe_filename(name: str) -> str:
        """Convert a person's name to a safe filename stem."""
        safe = "".join(c if c.isalnum() or c in " _-" else "_" for c in name)
        return safe.strip().replace(" ", "_") or "resume"

    # -----------------------------------------------------------------------
    def save_data(self, resume: Resume, filename: str = "") -> str:
        """
        Serialize *resume* to JSON and write to data/<filename>.json.
        If *filename* is empty the person's name is used.
        Returns the full path of the saved file.
        Raises IOError / json.JSONEncodeError on failure.
        """
        if not filename:
            filename = self._safe_filename(resume.person.name)

        if not filename.endswith(".json"):
            filename += ".json"

        path = DATA_DIR / filename

        try:
            data = resume.to_dict()
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        except (OSError, TypeError) as exc:
            raise IOError(f"Failed to save data: {exc}") from exc

        return str(path)

    # -----------------------------------------------------------------------
    def load_data(self, filename: str, resume: Resume) -> None:
        """
        Load JSON from data/<filename> into *resume* (in-place).
        *filename* can be just the stem, e.g. 'John_Doe',
        or a full path.
        Raises FileNotFoundError / ValueError on failure.
        """
        # Accept a bare name, a name + .json, or a full path
        path = Path(filename)
        if not path.is_absolute():
            if not filename.endswith(".json"):
                filename += ".json"
            path = DATA_DIR / filename

        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Corrupted JSON file: {exc}") from exc
        except OSError as exc:
            raise IOError(f"Cannot read file: {exc}") from exc

        resume.load_from_dict(data)

    # -----------------------------------------------------------------------
    @staticmethod
    def list_saved() -> list[str]:
        """Return a sorted list of saved JSON filenames (stems only)."""
        return sorted(p.stem for p in DATA_DIR.glob("*.json"))

    # -----------------------------------------------------------------------
    @staticmethod
    def delete_saved(filename: str) -> None:
        """Delete a saved JSON file. Raises FileNotFoundError if absent."""
        if not filename.endswith(".json"):
            filename += ".json"
        path = DATA_DIR / filename
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        path.unlink()
