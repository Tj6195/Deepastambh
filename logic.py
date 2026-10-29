"""logic.py: skill-gap and learning-plan functions for Deepstambh.
Plain Python only (no Streamlit) so it is easy to read and test."""
import json
import math

# The skill order used for plans: basic first, advanced last
LEVEL_ORDER = {"basic": 0, "intermediate": 1, "advanced": 2}

# Assumption: the "estimated_weeks" in careers.json are written for a learner
# studying about 10 hours per week. This is a planning assumption, not a measured figure.
BASELINE_HOURS = 10


def load_careers(path="careers.json"):
    """Load the careers file. Returns {} if the file is missing or broken."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("careers", {})
    except (OSError, ValueError):
        return {}


def compare_skills(career, student_skills):
    """Return (present, missing, match_percent) for one career.
    `career` is one career dict; `student_skills` may be empty or None."""
    required = career.get("required_skills", []) if career else []
    have = set(student_skills or [])
    present = [s for s in required if s in have]
    missing = [s for s in required if s not in have]
    percent = round(100 * len(present) / len(required)) if required else 0
    return present, missing, percent


def build_plan(career, missing, hours_per_week):
    """Return (plan, total_weeks, study_weeks).
    plan = list of dicts ordered basic -> advanced.
    total_weeks = sum of the dataset's weeks (at ~BASELINE_HOURS per week).
    study_weeks = total scaled to the student's own weekly hours."""
    levels = career.get("skill_levels", {}) if career else {}
    resources = career.get("learning_resources", {}) if career else {}
    weeks = career.get("estimated_weeks", {}) if career else {}

    plan = []
    for skill in (missing or []):
        plan.append({
            "skill": skill,
            "level": levels.get(skill, "intermediate"),
            "resource": resources.get(skill, "Free resource to be added"),
            "weeks": weeks.get(skill, 0),
        })
    # sorted() keeps the original order for skills with the same level
    plan.sort(key=lambda item: LEVEL_ORDER.get(item["level"], 1))

    total_weeks = sum(item["weeks"] for item in plan)
    try:
        hours = max(1, int(hours_per_week))
    except (TypeError, ValueError):
        hours = BASELINE_HOURS
    study_weeks = math.ceil(total_weeks * BASELINE_HOURS / hours) if total_weeks else 0
    return plan, total_weeks, study_weeks


def plan_to_text(name, career_name, percent, present, plan, study_weeks, hours):
    """Build the plain-text version of the plan for download."""
    lines = ["DEEPSTAMBH: LEARNING PLAN", "=" * 26]
    lines.append("Student: " + (name or "Not given"))
    lines.append("Target career: " + career_name)
    lines.append("Skill match: " + str(percent) + "%")
    lines.append("Skills you have: " + (", ".join(present) if present else "None selected"))
    lines.append("")
    if not plan:
        lines.append("No skill gaps found for this career.")
    for i, item in enumerate(plan, start=1):
        lines.append(f"{i}. {item['skill']} ({item['level']})")
        lines.append(f"   Resource: {item['resource']}")
        lines.append(f"   Estimated weeks: {item['weeks']}")
    lines.append("")
    lines.append(f"Time to close all gaps at {hours} hours/week: about {study_weeks} weeks")
    lines.append(f"(Weeks per skill assume about {BASELINE_HOURS} hours/week. Data to be validated.)")
    return "\n".join(lines)
