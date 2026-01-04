import base64
import streamlit as st
from openai import OpenAI
from PyPDF2 import PdfReader
from docx import Document
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

IMAGE_FILE_NAME = "background.png"

from prompts import (
    career_analysis_prompt,
    roadmap_prompt,
    more_careers_prompt,
    career_details_prompt
)

# =========================
# Load API Key
# =========================
client = OpenAI(api_key=st.secrets["openai"]["api_key"])

# ============================
# BACKGROUND IMAGE
# ============================
def get_base64(file_path):
    try:
        with open(file_path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except Exception:
        return None

bin_str = get_base64(IMAGE_FILE_NAME)
if bin_str:
    st.markdown(f"""
    <style>
    [data-testid="stAppViewContainer"] {{
        background: url("data:image/png;base64,{bin_str}") !important;
        background-size: cover;
        background-position: center;
    }}
    .main > div {{
        background: rgba(255, 255, 255, 0.75);
        border-radius: 12px;
        padding: 14px;
    }}
    </style>
    """, unsafe_allow_html=True)

# =========================
# Session State
# =========================
if "ai_output" not in st.session_state:
    st.session_state.ai_output = ""
if "profile" not in st.session_state:
    st.session_state.profile = ""
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# =========================
# Helper Functions
# =========================
def extract_resume_text(file):
    if not file:
        return ""
    text = ""
    if file.type == "application/pdf":
        reader = PdfReader(file)
        for page in reader.pages:
            if page.extract_text():
                text += page.extract_text()
    elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        doc = Document(file)
        for para in doc.paragraphs:
            text += para.text + "\n"
    return text

def get_ai_response(prompt, tokens=1500):
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=tokens,
        temperature=0.7
    )
    return response.choices[0].message.content

def generate_pdf(text, filename="career_roadmap.pdf"):
    doc = SimpleDocTemplate(filename, rightMargin=50, leftMargin=50, topMargin=50, bottomMargin=50)
    styles = getSampleStyleSheet()
    h1 = ParagraphStyle(name='Heading1', parent=styles['Heading1'], fontSize=18, spaceAfter=12, leading=22)
    h2 = ParagraphStyle(name='Heading2', parent=styles['Heading2'], fontSize=14, spaceAfter=8, leading=18)
    normal = ParagraphStyle(name='Normal', parent=styles['Normal'], fontSize=12, spaceAfter=6, leading=15)
    bullet = ParagraphStyle(name='Bullet', parent=styles['Normal'], leftIndent=20, bulletIndent=10, bulletFontSize=12, spaceAfter=4)

    content = []
    lines = text.split("\n")
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line.startswith("Career Path") or line.startswith("Final Verdict"):
            content.append(Paragraph(line, h2))
            content.append(Spacer(1, 4))
        elif line.startswith("-") or line.startswith("*"):
            content.append(Paragraph(line, bullet))
        else:
            content.append(Paragraph(line, normal))
    content.append(PageBreak())
    doc.build(content)
    return filename

# =========================
# Streamlit UI
# =========================
st.set_page_config(page_title="Career Path Stimulator", layout="centered")
st.title("🚀 Career Path Stimulator")
st.write("AI-powered career, salary & lifestyle simulation")

# =========================
# Profile Form
# =========================
with st.form("profile_form"):
    st.subheader("👤 Basic Profile")
    name = st.text_input("Name")
    age = st.number_input("Age", 12, 60, 12)
    interests = st.text_area("Interests (e.g., AI, Finance, Design)")
    skills = st.text_area("Skills (e.g., Python, Excel, Writing)")
    education = st.selectbox("Education", ["High School", "Undergraduate", "Graduate", "Other"])

    st.subheader("🌍 Preferences")
    country = st.selectbox("Country", ["India", "USA", "Germany", "UK", "Canada", "Other"])
    city = st.text_input("City (Optional)")
    people = st.number_input("People to support", 1, 10, 1)
    lifestyle = st.selectbox("Lifestyle", ["Basic", "Comfortable", "Luxury"])
    min_salary = st.number_input("Minimum Expected Salary", 0, step=5000)
    currency = st.selectbox("Currency", ["USD", "EUR", "INR"])
    employment_demand = st.selectbox("Preferred Employment Demand", ["High", "Medium", "Low"])
    future_security = st.selectbox("Future Job Security Importance", ["Very Important", "Moderate", "Not Important"])

    resume_file = st.file_uploader("Upload Resume (PDF/DOCX)", ["pdf", "docx"])
    scenario = st.text_area("Optional Scenario (e.g., if I learn AI for 2 years...)", "")

    submitted = st.form_submit_button("Generate Career Analysis")

# =========================
# On Submit
# =========================
if submitted:
    resume_text = extract_resume_text(resume_file)
    profile = f"""
Name: {name}
Age: {age}
Interests: {interests}
Skills: {skills}
Education: {education}

Country: {country}, City: {city}
People to support: {people}
Lifestyle: {lifestyle}
Minimum Salary: {min_salary} {currency}
Employment Demand: {employment_demand}
Future Security Importance: {future_security}

Resume:
{resume_text}
"""
    st.session_state.profile = profile
    with st.spinner("🔍 Analyzing careers..."):
        ai_result = get_ai_response(career_analysis_prompt(profile, scenario), tokens=2000)
        st.session_state.ai_output = ai_result
        st.session_state.chat_history = [{"role": "assistant", "content": ai_result}]

# =========================
# Polished Output Display
# =========================
if st.session_state.ai_output:
    st.subheader("🎯 Career Analysis Result")
    career_lines = st.session_state.ai_output.split("\n")
    for line in career_lines:
        line = line.strip()
        if not line:
            continue
        if line.startswith("Career Path"):
            st.markdown(f"---\n### 🚀 {line}")
        elif line.endswith("Roadmap") or line.endswith("Range") or line.endswith("Security") or line.endswith("Balance") or line.endswith("Competition"):
            st.markdown(f"#### 📝 {line}")
        elif line.startswith("Final Verdict"):
            st.markdown(f"### ✅ {line}")
        elif line.startswith("-") or line.startswith("*"):
            st.markdown(f"• {line[1:].strip()}")
        else:
            st.markdown(line)

# =========================
# Follow-up Chat
# =========================
st.divider()
st.subheader("💬 Ask Follow-up / Continue Analysis")
user_input = st.text_input("Enter your follow-up question or continuation")

if st.button("Send Follow-up"):
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=st.session_state.chat_history,
        max_tokens=1500,
        temperature=0.7
    )
    ai_reply = response.choices[0].message.content
    st.session_state.chat_history.append({"role": "assistant", "content": ai_reply})
    st.session_state.ai_output = ai_reply
    st.experimental_rerun()

# =========================
# Next Actions
# =========================
if st.session_state.profile:
    st.divider()
    st.subheader("🤔 Next Actions")
    choice = st.radio(
        "Choose an option",
        [
            "Know more about a specific career",
            "Get more career opportunities",
            "Generate a detailed AI roadmap"
        ]
    )

    if choice == "Know more about a specific career":
        career_name = st.text_input("Enter Career Name")
        if st.button("Get Details"):
            detail_text = get_ai_response(career_details_prompt(career_name))
            st.markdown("### 💡 Career Details")
            st.markdown(detail_text)

    if choice == "Get more career opportunities":
        if st.button("Show More Careers"):
            more_text = get_ai_response(more_careers_prompt(st.session_state.profile))
            st.markdown("### 📋 More Career Opportunities")
            st.markdown(more_text)

    if choice == "Generate a detailed AI roadmap":
        selected_career = st.text_input("Career for Roadmap")
        edu_level = st.selectbox("Current Education Level", ["High School", "Undergraduate", "Graduate", "Other"])
        if st.button("Generate Roadmap"):
            roadmap_text = get_ai_response(roadmap_prompt(st.session_state.profile, selected_career, edu_level), tokens=2000)
            st.subheader("🗺️ AI Career Roadmap")
            st.markdown(roadmap_text)
            pdf_file = generate_pdf(roadmap_text)
            with open(pdf_file, "rb") as f:
                st.download_button(
                    "📄 Download Roadmap as PDF",
                    f,
                    file_name="career_roadmap.pdf",
                    mime="application/pdf"
                )
