"""app.py: Streamlit interface for Deepstambh."""
import base64
import html
import time
from pathlib import Path

import streamlit as st

import logic

# Set to False to switch off every animation (see README notes)
ANIMATIONS_ON = True

BASE_DIR = Path(__file__).parent
LOGO_PATH = BASE_DIR / "logo.png"
YEARS = ["First Year", "Second Year", "Third Year", "Final Year", "Postgraduate"]

st.set_page_config(page_title="Deepstambh", page_icon="🔦", layout="centered")

# ------------------------------------------------------------------
# ALL CSS LIVES IN THIS ONE BLOCK
# ------------------------------------------------------------------
CSS = """
html, body, [class*="css"] { font-family: "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }
.block-container { padding-top: 1.5rem; max-width: 820px; }

/* Keyframes (elements stay visible if animations fail) */
@keyframes fadeUp { from { opacity: 0; transform: translateY(12px); } to { opacity: 1; transform: translateY(0); } }
@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }

/* Hero */
.hero { text-align: center; padding: 1rem 0 0.5rem 0; }
.logo-wrap { position: relative; width: 200px; height: 200px; margin: 0 auto; display: flex; align-items: center; justify-content: center; }
.beam { position: absolute; width: 200px; height: 200px; border-radius: 50%; z-index: 0;
  background: conic-gradient(from 0deg, rgba(245,184,65,0.28), rgba(245,184,65,0) 45deg, rgba(0,0,0,0) 180deg, rgba(245,184,65,0.28) 180deg, rgba(245,184,65,0) 225deg, rgba(0,0,0,0) 360deg);
  animation: spin 6s linear infinite; }
.logo-img { position: relative; z-index: 1; width: 130px; height: 130px; border-radius: 50%; object-fit: cover; }
.logo-emoji { position: relative; z-index: 1; font-size: 64px; }
.hero h1 { color: #F5B841; font-size: 1.9rem; line-height: 1.25; margin: 0.4rem 0 0.3rem 0; animation: fadeUp 0.8s ease-out both; }
.hero p { color: #D5DCE8; font-size: 1.05rem; margin: 0; animation: fadeUp 0.8s ease-out 0.15s both; }

/* Section containers */
div[data-testid="stVerticalBlockBorderWrapper"], .section-card {
  border-radius: 16px; box-shadow: 0 6px 18px rgba(0,0,0,0.25); padding: 0.5rem; }
.section-card { background: #12294A; padding: 1rem 1.2rem; margin: 0.6rem 0; }
.section-title { color: #F5B841; font-size: 1.25rem; font-weight: 700; margin: 0.2rem 0 0.6rem 0; }

/* Skill chips */
.chip { display: inline-block; padding: 0.3rem 0.8rem; margin: 0.25rem 0.3rem 0.25rem 0; border-radius: 999px;
  font-size: 0.9rem; font-weight: 600; animation: fadeUp 0.5s ease-out both; }
.chip-have { background: rgba(61,214,140,0.18); border: 1px solid #3DD68C; color: #9CF5C6; }
.chip-miss { background: rgba(255,159,67,0.18); border: 1px solid #FF9F43; color: #FFC98A; }

/* Plan cards */
.plan-card { background: #12294A; border-left: 4px solid #F5B841; border-radius: 14px; padding: 0.9rem 1.1rem; margin: 0.6rem 0;
  box-shadow: 0 4px 14px rgba(0,0,0,0.25); transition: transform 0.2s ease, box-shadow 0.2s ease; animation: fadeUp 0.5s ease-out both; }
.plan-card:hover { transform: translateY(-3px); box-shadow: 0 10px 22px rgba(0,0,0,0.35); }
.plan-card h4 { margin: 0 0 0.3rem 0; color: #FFFFFF; font-size: 1.05rem; }
.plan-card p { margin: 0.1rem 0; color: #D5DCE8; font-size: 0.92rem; }
.badge { display: inline-block; padding: 0.1rem 0.6rem; border-radius: 999px; font-size: 0.75rem; font-weight: 700; margin-left: 0.5rem; color: #0B1F3A; }
.badge-basic { background: #8FD3FF; } .badge-intermediate { background: #F5B841; } .badge-advanced { background: #FF9F43; }

/* Empty state */
.empty { text-align: center; color: #D5DCE8; padding: 1.5rem 1rem; }
.empty .big { font-size: 2.2rem; }

/* Metric, buttons */
div[data-testid="stMetricValue"] { font-size: 3.2rem; color: #F5B841; }
.stButton > button, .stDownloadButton > button { border-radius: 10px; transition: transform 0.2s ease, box-shadow 0.2s ease; }
.stButton > button:hover, .stDownloadButton > button:hover { transform: translateY(-2px); box-shadow: 0 6px 14px rgba(0,0,0,0.35); }
button[kind="primary"], button[kind="primary"] p { color: #0B1F3A !important; font-weight: 700; }

/* Footer */
.footer { text-align: center; color: #AEB9CB; font-size: 0.85rem; margin: 2rem 0 1rem 0; }

/* Mobile */
@media (max-width: 600px) { .hero h1 { font-size: 1.45rem; } .logo-wrap, .beam { width: 160px; height: 160px; } .logo-img { width: 105px; height: 105px; } }

/* Reduced motion: turn every animation off */
@media (prefers-reduced-motion: reduce) { *, *::before, *::after { animation: none !important; transition: none !important; } }
"""
if not ANIMATIONS_ON:
    CSS += "\n*, *::before, *::after { animation: none !important; transition: none !important; }"

st.markdown(f"<style>{CSS}</style>", unsafe_allow_html=True)


# ------------------------------------------------------------------
# Small helpers that build HTML
# ------------------------------------------------------------------
def logo_html():
    """Use logo.png if it exists, otherwise a light-themed emoji."""
    try:
        if LOGO_PATH.exists():
            data = base64.b64encode(LOGO_PATH.read_bytes()).decode()
            return f'<img class="logo-img" src="data:image/png;base64,{data}" alt="Deepstambh logo">'
    except OSError:
        pass
    return '<span class="logo-emoji">🔦</span>'


def chips_html(skills, css_class):
    """Chips fade in one after another using staggered delays."""
    return "".join(
        f'<span class="chip {css_class}" style="animation-delay:{i * 0.08:.2f}s">{html.escape(s)}</span>'
        for i, s in enumerate(skills)
    )


def section_title(icon, text):
    st.markdown(f'<div class="section-title">{icon} {text}</div>', unsafe_allow_html=True)


def empty_state(message):
    st.markdown(f'<div class="section-card empty"><div class="big">🧭</div>{message}</div>', unsafe_allow_html=True)


# ------------------------------------------------------------------
# Load data (stop politely if the file is missing)
# ------------------------------------------------------------------
careers = logic.load_careers(str(BASE_DIR / "careers.json"))
if not careers:
    st.error("Could not load careers.json. Please check that the file is in the project folder.")
    st.stop()
career_names = list(careers.keys())

# Default values for the widgets
st.session_state.setdefault("name", "")
st.session_state.setdefault("year", "Third Year")
st.session_state.setdefault("career", career_names[0])
st.session_state.setdefault("skills", [])
st.session_state.setdefault("hours", 8)
st.session_state.setdefault("result", None)
st.session_state.setdefault("animate", False)


def fill_sample():
    """Button callback: fill in a demo profile."""
    st.session_state.name = "Sample Student"
    st.session_state.year = "Third Year"
    st.session_state.career = "Data Analyst"
    st.session_state.skills = ["Excel", "SQL Basics", "Python Basics"]
    st.session_state.hours = 8


def clear_skills():
    """Selected skills belong to one career, so clear them when the career changes."""
    st.session_state.skills = []


# ------------------------------------------------------------------
# Hero
# ------------------------------------------------------------------
st.markdown(
    f"""<div class="hero"><div class="logo-wrap"><div class="beam"></div>{logo_html()}</div>
<h1>Deepstambh: a fixed point for your career decisions</h1>
<p>See your skill gaps. Follow a plan. Decide with clear information.</p></div>""",
    unsafe_allow_html=True,
)

tab1, tab2, tab3 = st.tabs(["Your Profile", "Skill Gaps", "Learning Plan"])

# ------------------------------------------------------------------
# Tab 1: Your Profile
# ------------------------------------------------------------------
with tab1:
    with st.container(border=True):
        section_title("👤", "Your Profile")
        st.button("Try a sample student", on_click=fill_sample)
        st.text_input("Your name (optional)", key="name")
        st.selectbox("Year of study", YEARS, key="year")
        st.selectbox("Target career", career_names, key="career", on_change=clear_skills)
        career = careers[st.session_state.career]
        st.multiselect("Skills you already have", career.get("required_skills", []), key="skills")
        if not st.session_state.skills:
            st.caption("🌱 No skills selected yet. Pick what you know, or leave it empty to see the full plan.")
        st.slider("Hours per week available for learning", 2, 20, key="hours")
        generate = st.button("Generate my plan", type="primary")

    if generate:
        try:
            with st.spinner("Finding your skill gaps..."):
                if ANIMATIONS_ON:
                    time.sleep(0.6)
                present, missing, percent = logic.compare_skills(career, st.session_state.skills)
                plan, total_weeks, study_weeks = logic.build_plan(career, missing, st.session_state.hours)
            st.session_state.result = {
                "name": st.session_state.name.strip(), "career": st.session_state.career,
                "hours": st.session_state.hours, "present": present, "missing": missing,
                "percent": percent, "plan": plan, "total_weeks": total_weeks, "study_weeks": study_weeks,
            }
            st.session_state.animate = ANIMATIONS_ON
            st.toast("Plan ready", icon="✅")
            st.info("Your plan is ready. Open the 'Skill Gaps' and 'Learning Plan' tabs.")
        except Exception:
            st.error("Something went wrong while building your plan. Please try again.")

result = st.session_state.result

# ------------------------------------------------------------------
# Tab 2: Skill Gaps
# ------------------------------------------------------------------
with tab2:
    if not result:
        empty_state("Nothing to show yet.<br>Fill in your profile and press <b>Generate my plan</b>.")
    else:
        pct = result["percent"]
        with st.container(border=True):
            section_title("🎯", f"Skill match for {html.escape(result['career'])}")
            metric_box = st.empty()
            bar_box = st.empty()
            if st.session_state.animate:
                # Count up from 0 to the real value in about 1 second
                for step in range(21):
                    value = round(pct * step / 20)
                    metric_box.metric("Match", f"{value}%")
                    bar_box.progress(value)
                    time.sleep(0.05)
                st.session_state.animate = False
            metric_box.metric("Match", f"{pct}%")
            bar_box.progress(pct)

        with st.container(border=True):
            section_title("✅", "Skills you have")
            if result["present"]:
                st.markdown(chips_html(result["present"], "chip-have"), unsafe_allow_html=True)
            else:
                st.caption("No skills selected, so every skill counts as a gap for now.")
            section_title("🧩", "Skills to build")
            if result["missing"]:
                st.markdown(chips_html(result["missing"], "chip-miss"), unsafe_allow_html=True)
            else:
                st.caption("No gaps found for this career. Well done!")

# ------------------------------------------------------------------
# Tab 3: Learning Plan
# ------------------------------------------------------------------
with tab3:
    if not result:
        empty_state("Your learning plan will appear here.<br>Start in the <b>Your Profile</b> tab.")
    elif not result["plan"]:
        empty_state("No skill gaps to plan for. Try another career!")
    else:
        with st.container(border=True):
            section_title("🗺️", "Your learning plan (basic to advanced)")
            cards = ""
            for i, item in enumerate(result["plan"]):
                cards += (
                    f'<div class="plan-card" style="animation-delay:{i * 0.1:.1f}s">'
                    f'<h4>{i + 1}. {html.escape(item["skill"])}'
                    f'<span class="badge badge-{item["level"]}">{html.escape(item["level"])}</span></h4>'
                    f'<p>📚 Free resource: {html.escape(item["resource"])}</p>'
                    f'<p>⏱️ Estimated: about {item["weeks"]} weeks</p></div>'
                )
            st.markdown(cards, unsafe_allow_html=True)

        with st.container(border=True):
            section_title("⏳", "Time to close all gaps")
            st.metric(f"At {result['hours']} hours per week", f"about {result['study_weeks']} weeks")
            st.caption(f"Each skill's weeks assume about {logic.BASELINE_HOURS} hours per week. This is a rough planning guide.")
            text = logic.plan_to_text(result["name"], result["career"], result["percent"],
                                      result["present"], result["plan"], result["study_weeks"], result["hours"])
            st.download_button("Download plan (.txt)", data=text, file_name="deepstambh_plan.txt", mime="text/plain")

# Footer
st.markdown('<div class="footer">Prototype for a pilot with 73 students. Data to be validated.</div>', unsafe_allow_html=True)
