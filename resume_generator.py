"""
resume_generator.py
-------------------
A lightweight wrapper around Resume.export_resume() that handles
filename construction and output-directory management.

This keeps gui.py clean; all export logic lives here.
"""

import os
from pathlib import Path
from models import Resume


RESUMES_DIR = Path(__file__).parent / "resumes"
RESUMES_DIR.mkdir(exist_ok=True)


class ResumeGenerator:
    """
    Orchestrates resume generation and export.

    Usage:
        gen = ResumeGenerator(resume)
        txt_path = gen.export_txt()
        pdf_path = gen.export_pdf()
    """

    def __init__(self, resume: Resume):
        self.resume = resume

    # -----------------------------------------------------------------------
    def _base_filename(self) -> str:
        """Derive a filesystem-safe base name from the person's name."""
        name = self.resume.person.name.strip().replace(" ", "_") or "resume"
        return "".join(c for c in name if c.isalnum() or c in "_-")

    # -----------------------------------------------------------------------
    def export_txt(self, directory: str = "") -> str:
        """
        Write a plain-text resume to *directory* (default: resumes/).
        Returns the full output path.
        Raises ValueError / IOError on failure.
        """
        out_dir = Path(directory) if directory else RESUMES_DIR
        out_dir.mkdir(parents=True, exist_ok=True)
        path = out_dir / f"{self._base_filename()}_resume.txt"

        try:
            self.resume.export_resume(str(path), fmt="txt")
        except Exception as exc:
            raise IOError(f"TXT export failed: {exc}") from exc

        return str(path)

    # -----------------------------------------------------------------------
    def export_pdf(self, directory: str = "") -> str:
        """
        Write a PDF resume to *directory* (default: resumes/).
        Returns the full output path.
        Raises ValueError / IOError on failure.
        """
        out_dir = Path(directory) if directory else RESUMES_DIR
        out_dir.mkdir(parents=True, exist_ok=True)
        path = out_dir / f"{self._base_filename()}_resume.pdf"

        try:
            self.resume.export_resume(str(path), fmt="pdf")
        except Exception as exc:
            raise IOError(f"PDF export failed: {exc}") from exc

        return str(path)

    # -----------------------------------------------------------------------
    def get_preview_text(self) -> str:
        """Return the plain-text preview string."""
        return self.resume.preview_resume()
