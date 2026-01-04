# prompts.py

def career_analysis_prompt(profile, scenario):
    return f"""
You are an expert career advisor.
User Profile:
{profile}
Scenario: {scenario}

Generate 3 suitable career paths.
Include:
- Job Role and Career Roadmap
- Employment Demand (Current & Future)
- Future Security (5–10 years)
- Salary Range (country-specific)
- Living Expenses vs Salary
- Feasibility for supporting given number of people
- Work-life balance
- Risks and competition
- Final Verdict
Format clearly.
"""

def roadmap_prompt(profile, career, education_level):
    return f"""
You are an expert career counselor.
User Profile:
{profile}
Selected Career: {career}
Current Education Level: {education_level}

Generate a detailed career roadmap starting from this education level.
Include:
- Courses to take at each stage (High School, Undergraduate, Postgraduate, etc.)
- Certifications
- Internships or projects
- Steps to reach mid-level and senior positions
- Online resources
- Skills development
Format in structured sections.
"""

def more_careers_prompt(profile):
    return f"""
Based on this user profile, suggest 5 additional career opportunities.
Include:
- Job roles
- Estimated salary range
- Skills required
- Feasibility based on lifestyle and support requirements
Format clearly.
"""

def career_details_prompt(career_name):
    return f"""
Explain this career in detail:
{career_name}
Include:
- Job roles
- Growth opportunities
- Salary range
- Stability and future security
- Recommended education and skills
- Ideal candidate profile
"""
