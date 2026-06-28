# Resume Builder System

A GUI-based resume builder built with **Python 3.12+**, **Tkinter**, **OOP**, and **ReportLab**.

---

## Folder Structure

```
ResumeBuilder/
├── main.py              # Entry point — run this
├── gui.py               # All Tkinter UI code (ResumeApp class)
├── models.py            # Data classes: Person, Education, Skill, Certification, Resume
├── file_manager.py      # JSON save/load (FileManager class)
├── resume_generator.py  # Export orchestration (ResumeGenerator class)
├── requirements.txt     # pip dependencies
├── assets/              # Place custom icons/images here
├── data/                # Auto-created — stores saved JSON resumes
└── resumes/             # Auto-created — stores exported TXT/PDF files
```

---

## Requirements

| Package    | Purpose                         |
|------------|---------------------------------|
| reportlab  | PDF resume generation           |
| Pillow     | Profile photo preview (optional)|

Tkinter comes bundled with the standard Python installer.

---

## Installation

### 1. Install Python 3.12+
Download from https://www.python.org/downloads/

Make sure to check **"Add Python to PATH"** during installation.

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

Or individually:

```bash
pip install reportlab Pillow
```

---

## Running the Application

```bash
cd ResumeBuilder
python main.py
```

---

## Step-by-Step Usage Guide

1. **Personal Tab** — Fill in Name (required), Email (required), Phone, Address, LinkedIn, GitHub, and Career Objective. Click the photo placeholder to add a profile picture.

2. **Education Tab** — Enter Degree, Institution, Year, CGPA and click **➕ Add Education**. Repeat for each qualification. Click a row to load it back into the fields for editing.

3. **Skills Tab** — Type a skill and click **➕ Add**. Remove with **🗑 Remove**.

4. **Certifications Tab** — Enter Certificate Name, Organization, Year and click **➕ Add Certification**.

5. **Settings Tab** — Choose a template (classic / modern / minimal). Enable auto-save. Search and load previously saved resumes.

6. **Toolbar buttons:**
   - **👁 Preview** — Renders the resume in the right-hand preview pane.
   - **💾 Save** — Saves all data to `data/<name>.json`.
   - **📤 Export TXT** — Saves a plain-text resume to `resumes/`.
   - **📄 Export PDF** — Generates a styled PDF via ReportLab.
   - **🗑 Clear** — Resets the entire form.
   - **🌓 Theme** — Toggles between Light and Dark mode.

---

## Features

- ✅ Full OOP architecture (Person, Education, Skill, Certification, Resume, FileManager)
- ✅ JSON persistence with save / load / delete
- ✅ TXT and PDF export
- ✅ Dark / Light mode toggle
- ✅ Profile photo support (requires Pillow)
- ✅ Auto-save every 60 seconds
- ✅ Search saved resumes
- ✅ Input validation (email format, 10-digit phone, required fields)
- ✅ Friendly error dialogs
- ✅ Scrollable personal info panel
- ✅ Treeview for education & certifications

---

## Class Reference

| Class              | File                  | Role                                             |
|--------------------|-----------------------|--------------------------------------------------|
| `Person`           | models.py             | Stores contact & objective; validates email/phone|
| `Education`        | models.py             | Single degree record; list managed by Resume     |
| `Skill`            | models.py             | Single skill entry                               |
| `Certification`    | models.py             | Single certification entry                       |
| `Resume`           | models.py             | Aggregates all data; generates & exports resume  |
| `FileManager`      | file_manager.py       | JSON read/write with error handling              |
| `ResumeGenerator`  | resume_generator.py   | Thin wrapper; resolves output paths              |
| `ResumeApp`        | gui.py                | Main Tkinter window; all UI logic                |
