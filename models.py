"""
models.py - Data model classes for Resume Builder System
Contains: Person, Education, Skill, Certification, Project, Experience, Resume
"""

import re
from datetime import datetime


# ---------------------------------------------------------------------------
# Person
# ---------------------------------------------------------------------------
class Person:
    """Stores personal/contact information for the resume owner."""

    def __init__(self):
        self.name       = ""
        self.email      = ""
        self.phone      = ""
        self.address    = ""
        self.linkedin   = ""
        self.github     = ""
        self.objective  = ""
        self.photo_path = ""

    @staticmethod
    def validate_email(email):
        return bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email))

    @staticmethod
    def validate_phone(phone):
        return phone.isdigit() and len(phone) == 10

    def update_details(self, **kwargs):
        if "email" in kwargs and kwargs["email"]:
            if not self.validate_email(kwargs["email"]):
                raise ValueError("Invalid email address.")
        if "phone" in kwargs and kwargs["phone"]:
            if not self.validate_phone(kwargs["phone"]):
                raise ValueError("Phone must be exactly 10 digits.")
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def get_details(self):
        return {
            "name": self.name, "email": self.email, "phone": self.phone,
            "address": self.address, "linkedin": self.linkedin,
            "github": self.github, "objective": self.objective,
            "photo_path": self.photo_path,
        }

    def is_valid(self):
        if not self.name.strip():  return False, "Name is required."
        if not self.email.strip(): return False, "Email is required."
        if not self.validate_email(self.email): return False, "Invalid email address."
        if self.phone and not self.validate_phone(self.phone):
            return False, "Phone must be exactly 10 digits."
        return True, ""


# ---------------------------------------------------------------------------
# Education
# ---------------------------------------------------------------------------
class Education:
    def __init__(self, degree="", institution="", passing_year="", cgpa=""):
        self.degree       = degree
        self.institution  = institution
        self.passing_year = passing_year
        self.cgpa         = cgpa

    def add_record(self, degree, institution, passing_year, cgpa):
        self.degree = degree.strip(); self.institution = institution.strip()
        self.passing_year = passing_year.strip(); self.cgpa = cgpa.strip()

    def remove_record(self):
        self.degree = self.institution = self.passing_year = self.cgpa = ""

    def to_dict(self):
        return {"degree": self.degree, "institution": self.institution,
                "passing_year": self.passing_year, "cgpa": self.cgpa}

    @classmethod
    def from_dict(cls, d):
        return cls(d.get("degree",""), d.get("institution",""),
                   d.get("passing_year",""), d.get("cgpa",""))

    def __str__(self):
        return f"{self.degree} | {self.institution} | {self.passing_year} | CGPA: {self.cgpa}"


# ---------------------------------------------------------------------------
# Skill
# ---------------------------------------------------------------------------
class Skill:
    def __init__(self, skill_name=""):
        self.skill_name = skill_name

    def add_skill(self, name):    self.skill_name = name.strip()
    def remove_skill(self):       self.skill_name = ""
    def to_dict(self):            return {"skill_name": self.skill_name}
    @classmethod
    def from_dict(cls, d):        return cls(d.get("skill_name",""))
    def __str__(self):            return self.skill_name


# ---------------------------------------------------------------------------
# Certification
# ---------------------------------------------------------------------------
class Certification:
    def __init__(self, certificate_name="", organization="", completion_year=""):
        self.certificate_name = certificate_name
        self.organization     = organization
        self.completion_year  = completion_year

    def add_certificate(self, name, org, year):
        self.certificate_name = name.strip()
        self.organization = org.strip()
        self.completion_year = year.strip()

    def remove_certificate(self):
        self.certificate_name = self.organization = self.completion_year = ""

    def to_dict(self):
        return {"certificate_name": self.certificate_name,
                "organization": self.organization,
                "completion_year": self.completion_year}

    @classmethod
    def from_dict(cls, d):
        return cls(d.get("certificate_name",""), d.get("organization",""),
                   d.get("completion_year",""))

    def __str__(self):
        return f"{self.certificate_name} | {self.organization} | {self.completion_year}"


# ---------------------------------------------------------------------------
# Project  (NEW)
# ---------------------------------------------------------------------------
class Project:
    """
    A single project entry.
    Attributes:
        title       - Project title
        tech_stack  - Technologies used (comma-separated)
        duration    - e.g. "Jan 2024 – Mar 2024"
        description - What the project does / your role
        link        - GitHub / live URL (optional)
    """
    def __init__(self, title="", tech_stack="", duration="", description="", link=""):
        self.title       = title
        self.tech_stack  = tech_stack
        self.duration    = duration
        self.description = description
        self.link        = link

    def add_project(self, title, tech_stack, duration, description, link=""):
        self.title = title.strip(); self.tech_stack = tech_stack.strip()
        self.duration = duration.strip(); self.description = description.strip()
        self.link = link.strip()

    def remove_project(self):
        self.title = self.tech_stack = self.duration = self.description = self.link = ""

    def to_dict(self):
        return {"title": self.title, "tech_stack": self.tech_stack,
                "duration": self.duration, "description": self.description,
                "link": self.link}

    @classmethod
    def from_dict(cls, d):
        return cls(d.get("title",""), d.get("tech_stack",""), d.get("duration",""),
                   d.get("description",""), d.get("link",""))

    def __str__(self):
        return f"{self.title} | {self.tech_stack} | {self.duration}"


# ---------------------------------------------------------------------------
# Experience  (NEW)
# ---------------------------------------------------------------------------
class Experience:
    """
    A single work / internship experience entry.
    Attributes:
        job_title   - Role / designation
        company     - Company or organisation name
        location    - City / Remote
        start_date  - e.g. "Jun 2022"
        end_date    - e.g. "May 2024" or "Present"
        description - Key responsibilities and achievements
    """
    def __init__(self, job_title="", company="", location="",
                 start_date="", end_date="", description=""):
        self.job_title   = job_title
        self.company     = company
        self.location    = location
        self.start_date  = start_date
        self.end_date    = end_date
        self.description = description

    def add_experience(self, job_title, company, location, start_date, end_date, description):
        self.job_title   = job_title.strip()
        self.company     = company.strip()
        self.location    = location.strip()
        self.start_date  = start_date.strip()
        self.end_date    = end_date.strip()
        self.description = description.strip()

    def remove_experience(self):
        self.job_title = self.company = self.location = ""
        self.start_date = self.end_date = self.description = ""

    def to_dict(self):
        return {"job_title": self.job_title, "company": self.company,
                "location": self.location, "start_date": self.start_date,
                "end_date": self.end_date, "description": self.description}

    @classmethod
    def from_dict(cls, d):
        return cls(d.get("job_title",""), d.get("company",""), d.get("location",""),
                   d.get("start_date",""), d.get("end_date",""), d.get("description",""))

    def __str__(self):
        return f"{self.job_title} @ {self.company} ({self.start_date} – {self.end_date})"


# ---------------------------------------------------------------------------
# Resume  (aggregator)
# ---------------------------------------------------------------------------
class Resume:
    """Aggregates all resume sections and handles generation / export."""

    def __init__(self):
        self.person:        Person          = Person()
        self.educations:    list            = []
        self.experiences:   list            = []   # NEW
        self.projects:      list            = []   # NEW
        self.skills:        list            = []
        self.certifications:list            = []
        self.template:      str             = "classic"
        self.created_at:    str             = datetime.now().strftime("%Y-%m-%d %H:%M")

    # ---- Validation ---------------------------------------------------------
    def validate(self):
        ok, msg = self.person.is_valid()
        if not ok: return False, msg
        if not self.educations:
            return False, "At least one education entry is required."
        return True, ""

    # ---- Plain-text generation ----------------------------------------------
    def generate_resume(self) -> str:
        ok, msg = self.validate()
        if not ok:
            raise ValueError(msg)

        p = self.person
        W = 65
        lines = []

        # Header
        lines += ["=" * W, p.name.upper().center(W), "=" * W]

        # Contact – 3 items per line, separated by  |
        contact = []
        if p.email:    contact.append(f"Email: {p.email}")
        if p.phone:    contact.append(f"Phone: {p.phone}")
        if p.address:  contact.append(f"Address: {p.address}")
        if p.linkedin: contact.append(f"LinkedIn: {p.linkedin}")
        if p.github:   contact.append(f"GitHub: {p.github}")
        for i in range(0, len(contact), 3):
            lines.append("  |  ".join(contact[i:i+3]))
        lines.append("")

        # Objective
        if p.objective:
            lines += ["CAREER OBJECTIVE", "-"*40, p.objective, ""]

        # Experience
        if self.experiences:
            lines += ["EXPERIENCE", "-"*40]
            for exp in self.experiences:
                period = f"{exp.start_date} – {exp.end_date}" if exp.start_date else ""
                loc    = f"  |  {exp.location}" if exp.location else ""
                lines.append(f"  • {exp.job_title}  —  {exp.company}{loc}  [{period}]")
                if exp.description:
                    for line in exp.description.split("\n"):
                        if line.strip():
                            lines.append(f"      {line.strip()}")
            lines.append("")

        # Education
        lines += ["EDUCATION", "-"*40]
        for edu in self.educations:
            lines.append(f"  • {edu.degree}")
            lines.append(f"    {edu.institution}  |  Year: {edu.passing_year}  |  CGPA/Score: {edu.cgpa}")
        lines.append("")

        # Projects
        if self.projects:
            lines += ["PROJECTS", "-"*40]
            for proj in self.projects:
                tech = f"  [{proj.tech_stack}]" if proj.tech_stack else ""
                dur  = f"  ({proj.duration})" if proj.duration else ""
                lines.append(f"  • {proj.title}{tech}{dur}")
                if proj.description:
                    lines.append(f"    {proj.description}")
                if proj.link:
                    lines.append(f"    Link: {proj.link}")
            lines.append("")

        # Skills
        if self.skills:
            lines += ["SKILLS", "-"*40]
            lines.append("  " + ",  ".join(s.skill_name for s in self.skills if s.skill_name))
            lines.append("")

        # Certifications
        if self.certifications:
            lines += ["CERTIFICATIONS", "-"*40]
            for cert in self.certifications:
                lines.append(f"  • {cert.certificate_name}")
                lines.append(f"    Issued by: {cert.organization}  |  Year: {cert.completion_year}")
            lines.append("")

        lines.append("=" * W)
        return "\n".join(lines)

    def preview_resume(self) -> str:
        return self.generate_resume()

    def export_resume(self, path: str, fmt: str = "txt") -> None:
        if fmt == "txt":
            with open(path, "w", encoding="utf-8") as f:
                f.write(self.generate_resume())
        elif fmt == "pdf":
            self._export_pdf(path)
        else:
            raise ValueError(f"Unsupported format: {fmt}")

    # ---- PDF export ---------------------------------------------------------
    def _export_pdf(self, path: str) -> None:
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import (
            SimpleDocTemplate, Paragraph, Spacer, HRFlowable,
            Table, TableStyle, Image as RLImage,
        )
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib import colors
        from reportlab.lib.units import cm
        import os

        ok, msg = self.validate()
        if not ok:
            raise ValueError(msg)

        p   = self.person
        doc = SimpleDocTemplate(path, pagesize=A4,
                                leftMargin=2*cm, rightMargin=2*cm,
                                topMargin=2*cm,  bottomMargin=2*cm)
        styles = getSampleStyleSheet()

        name_sty = ParagraphStyle("N", parent=styles["Title"],
                                  fontSize=22, textColor=colors.HexColor("#2c3e50"), spaceAfter=4)
        sec_sty  = ParagraphStyle("S", parent=styles["Heading2"],
                                  fontSize=13, textColor=colors.HexColor("#2980b9"),
                                  spaceBefore=10, spaceAfter=3)
        normal   = styles["Normal"]
        contact_sty = ParagraphStyle("C", parent=normal, fontSize=9,
                                     textColor=colors.HexColor("#444444"), spaceAfter=2)
        sub_sty  = ParagraphStyle("Sub", parent=normal, fontSize=9,
                                  leftIndent=20, spaceAfter=3,
                                  textColor=colors.HexColor("#555555"))
        bul_sty  = ParagraphStyle("B", parent=normal, leftIndent=12, spaceAfter=2)

        story = []
        PW = A4[0] - 4*cm  # usable page width

        # ---- Header: name + horizontal contact | photo ----------------------
        contact = []
        if p.email:    contact.append(f"<b>Email:</b> {p.email}")
        if p.phone:    contact.append(f"<b>Phone:</b> {p.phone}")
        if p.address:  contact.append(f"<b>Address:</b> {p.address}")
        if p.linkedin: contact.append(f"<b>LinkedIn:</b> {p.linkedin}")
        if p.github:   contact.append(f"<b>GitHub:</b> {p.github}")

        left = [Paragraph(p.name, name_sty)]
        SEP = "  &nbsp;|&nbsp;  "
        for i in range(0, len(contact), 3):
            left.append(Paragraph(SEP.join(contact[i:i+3]), contact_sty))

        photo_cell = Spacer(3*cm, 3.5*cm)
        if p.photo_path and os.path.isfile(p.photo_path):
            try:
                photo_cell = RLImage(p.photo_path, width=3*cm, height=3.5*cm,
                                     kind="proportional")
            except Exception:
                pass

        ht = Table([[left, photo_cell]], colWidths=[PW - 3.5*cm, 3.5*cm])
        ht.setStyle(TableStyle([
            ("VALIGN",       (0,0),(-1,-1),"TOP"),
            ("ALIGN",        (1,0),(1,0),  "RIGHT"),
            ("LEFTPADDING",  (0,0),(-1,-1),0),
            ("RIGHTPADDING", (0,0),(-1,-1),0),
            ("TOPPADDING",   (0,0),(-1,-1),0),
            ("BOTTOMPADDING",(0,0),(-1,-1),0),
        ]))
        story.append(ht)
        story.append(HRFlowable(width="100%", thickness=1.5,
                                color=colors.HexColor("#2980b9"),
                                spaceAfter=6, spaceBefore=6))

        # ---- Objective ------------------------------------------------------
        if p.objective:
            story.append(Paragraph("Career Objective", sec_sty))
            story.append(Paragraph(p.objective, normal))

        # ---- Experience -----------------------------------------------------
        if self.experiences:
            story.append(Paragraph("Experience", sec_sty))
            for exp in self.experiences:
                period = f"{exp.start_date} – {exp.end_date}"
                loc    = f" | {exp.location}" if exp.location else ""
                story.append(Paragraph(
                    f"<b>{exp.job_title}</b> — {exp.company}{loc} "
                    f"<font size='9' color='#777777'>({period})</font>", bul_sty))
                if exp.description:
                    for line in exp.description.split("\n"):
                        if line.strip():
                            story.append(Paragraph(f"• {line.strip()}", sub_sty))

        # ---- Education ------------------------------------------------------
        story.append(Paragraph("Education", sec_sty))
        for edu in self.educations:
            story.append(Paragraph(f"<b>{edu.degree}</b> — {edu.institution}", bul_sty))
            story.append(Paragraph(f"Year: {edu.passing_year}    CGPA/Score: {edu.cgpa}", sub_sty))

        # ---- Projects -------------------------------------------------------
        if self.projects:
            story.append(Paragraph("Projects", sec_sty))
            for proj in self.projects:
                hdr = f"<b>{proj.title}</b>"
                if proj.tech_stack:
                    hdr += f"  <font size='9' color='#2980b9'>[{proj.tech_stack}]</font>"
                if proj.duration:
                    hdr += f"  <font size='9' color='#777777'>({proj.duration})</font>"
                story.append(Paragraph(hdr, bul_sty))
                if proj.description:
                    story.append(Paragraph(proj.description, sub_sty))
                if proj.link:
                    story.append(Paragraph(
                        f"<font color='#2980b9'>🔗 {proj.link}</font>", sub_sty))

        # ---- Skills ---------------------------------------------------------
        if self.skills:
            story.append(Paragraph("Skills", sec_sty))
            story.append(Paragraph(
                "  •  ".join(s.skill_name for s in self.skills if s.skill_name), normal))

        # ---- Certifications -------------------------------------------------
        if self.certifications:
            story.append(Paragraph("Certifications", sec_sty))
            for cert in self.certifications:
                story.append(Paragraph(
                    f"<b>{cert.certificate_name}</b> — {cert.organization} ({cert.completion_year})",
                    bul_sty))

        doc.build(story)

    # ---- Serialization ------------------------------------------------------
    def to_dict(self):
        return {
            "person":         self.person.get_details(),
            "educations":     [e.to_dict() for e in self.educations],
            "experiences":    [e.to_dict() for e in self.experiences],
            "projects":       [p.to_dict() for p in self.projects],
            "skills":         [s.to_dict() for s in self.skills],
            "certifications": [c.to_dict() for c in self.certifications],
            "template":       self.template,
            "created_at":     self.created_at,
        }

    def load_from_dict(self, data):
        self.person.update_details(**data.get("person", {}))
        self.educations     = [Education.from_dict(e)     for e in data.get("educations",     [])]
        self.experiences    = [Experience.from_dict(e)    for e in data.get("experiences",    [])]
        self.projects       = [Project.from_dict(p)       for p in data.get("projects",       [])]
        self.skills         = [Skill.from_dict(s)         for s in data.get("skills",         [])]
        self.certifications = [Certification.from_dict(c) for c in data.get("certifications", [])]
        self.template       = data.get("template", "classic")
        self.created_at     = data.get("created_at", self.created_at)
